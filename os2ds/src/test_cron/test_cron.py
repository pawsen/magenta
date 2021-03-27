#!/usr/bin/env python3

from io import StringIO
from json import loads
from contextlib import redirect_stdout

import django
import recurrence
from django.core.management import call_command
from os2datascanner.engine2.model.http import WebSource
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineRunner
from os2datascanner.engine2.rules.regex import RegexRule as TwegexRule
from os2datascanner.engine2.rules.rule import Sensitivity as Twensitivity
from os2datascanner.projects.admin.adminapp.models.organization_model import \
    Organization
from os2datascanner.projects.admin.adminapp.models.rules.regexrule_model import (
    RegexPattern, RegexRule)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner_model import \
    WebScanner
from os2datascanner.projects.admin.adminapp.models.sensitivity_level import \
    Sensitivity
from os2datascanner.utils.system_utilities import time_now


class StopHandling(Exception):
    pass


class PipelineTestRunner(PikaPipelineRunner):
    def handle_message(self, body, *, channel=None):
        yield from []

# NOTE: rule_pk and org_pk CANNOT be 1, as the default created CPRRule points to
# these keys. Thus the tearDown(or deletion) will fail when trying to delete the
# rule and org.
CONST_PK = 5
SCANNER_PK = 1 + CONST_PK
ORG_PK = 2 + CONST_PK
PATTERN_PK = 1 + CONST_PK
RULE_PK = 2 + CONST_PK

messages = []
# expected json message
obj = {
    "scan_tag": {
        "scanner": {"name": "Magenta", "pk": SCANNER_PK},
        "user": None,
        "organisation": {"name": "Magenta", "uuid": None},
        "time": None,  # set to now() in scanner_model.py
        "destination": "pipeline_collector",
    },
    "source": WebSource(
        url="https://www.magenta.dk", sitemap=None
    ).to_json_object(),
    "rule": TwegexRule(
        "fællesskaber", name=None, sensitivity=Twensitivity.NOTICE
    ).to_json_object(),
    "configuration": {"skip_mime_types": ["image/*"]},
    "progress": None,
}
messages.append((obj, "os2ds_scan_specs",))


def result_received(channel, method, properties, body):
    channel.basic_ack(method.delivery_tag)
    body = loads(body.decode("utf-8"))
    # overwrite transient fields
    body["scan_tag"]["time"] = None
    body["scan_tag"]["organisation"]["uuid"] = None
    messages.append((body, "os2ds_scan_specs"))
    if body:
        raise StopHandling()


class test():
    def setUp(self):
        # create organisations
        self.magenta_org = Organization(name="Magenta", pk=ORG_PK)
        self.magenta_org.save()

        # create scanners
        self.magenta_scanner = WebScanner(
            name="Magenta",
            url="https://www.magenta.dk",
            organization=self.magenta_org,
            validation_status=WebScanner.VALID,
            download_sitemap=False,
            do_last_modified_check=False,
            do_last_modified_check_head_request=False,
            pk=SCANNER_PK,
        )
        self.magenta_scanner_no_recur = WebScanner(
            name="Magenta_no_recurrence",
            url="https://www.magenta.dk",
            organization=self.magenta_org,
            validation_status=WebScanner.VALID,
            download_sitemap=False,
            do_last_modified_check_head_request=False,
            pk=SCANNER_PK+1,
        )
        self.magenta_scanner_tomorrow = WebScanner(
            name="Magenta_tomorrow",
            url="https://www.magenta.dk",
            organization=self.magenta_org,
            validation_status=WebScanner.VALID,
            download_sitemap=False,
            do_last_modified_check_head_request=False,
            pk=SCANNER_PK+2,
        )
        self.magenta_scanner.save()
        self.magenta_scanner_no_recur.save()
        self.magenta_scanner_tomorrow.save()

        # create regex cule
        self.reg1 = RegexPattern(pattern_string="fællesskaber", pk=PATTERN_PK)
        self.reg1.save()
        self.tr_set1 = RegexRule(
            name="MagentaTestRule1",
            sensitivity=Sensitivity.OK,
            organization=self.magenta_org,
            pk=RULE_PK,
        )
        self.tr_set1.patterns.add(self.reg1)
        self.tr_set1.save()
        self.magenta_scanner.rules.add(self.tr_set1)
        self.magenta_scanner_no_recur.rules.add(self.tr_set1)
        self.magenta_scanner_tomorrow.rules.add(self.tr_set1)
        self.magenta_scanner.save()
        self.magenta_scanner_no_recur.save()
        self.magenta_scanner_tomorrow.save()

        # create recurrence. Multiple recurernces can be given as a list
        tomorrow = (time_now().weekday() + 1) % 7
        rrule_daily = recurrence.Rule(recurrence.DAILY)
        rrule_tomorrow = recurrence.Rule(recurrence.WEEKLY, byday=tomorrow)
        self.magenta_scanner.schedule.rrules = [rrule_daily]
        self.magenta_scanner_tomorrow.schedule.rrules = [rrule_tomorrow]
        self.magenta_scanner.save()
        self.magenta_scanner_tomorrow.save()

        # open queue
        self.runner = PipelineTestRunner(
                read="os2ds_scan_specs",
                write=set(),
                heartbeat=6000)


    def tearDown(self):
        self.reg1.delete()
        self.tr_set1.delete()
        self.magenta_scanner.delete()
        self.magenta_scanner_no_recur.delete()
        self.magenta_scanner_tomorrow.delete()
        self.magenta_org.delete()
        self.runner.clear()


    def get_models(self):
        # run this to get models already existing in DB
        self.magenta_scanner = WebScanner.objects.filter(pk=SCANNER_PK).get()
        self.magenta_scanner_no_recur = WebScanner.objects.filter(pk=SCANNER_PK+1).get()
        self.magenta_scanner_tomorrow = WebScanner.objects.filter(pk=SCANNER_PK+2).get()
        self.tr_set1 = RegexRule.objects.filter(name="MagentaTestRule1").get()
        self.reg1 = \
            RegexPattern.objects.filter(pattern_string="fællesskaber").get()
        self.magenta_org = Organization.objects.filter(pk=ORG_PK).get()

        # open queue
        self.runner = PipelineTestRunner(
                read="os2ds_scan_specs",
                write=set(),
                heartbeat=6000)



    def test_cron(self):
        # capture stdout from cron.py
        # Another way is to redirect sys.stdout=buf=StringIO()
        # https://stackoverflow.com/a/1218951
        with StringIO() as buf, redirect_stdout(buf):
            call_command("cron", **{"now": True}, stdout=buf)
            self.output = buf.getvalue().rstrip()

        print(f"!!!! {self.output}")

        self.runner.channel.basic_consume("os2ds_scan_specs", result_received)
        try:
            self.runner.run_consumer()
        except StopHandling as e:
            print(
                messages[0][0],
                messages[1][0],
                "Wrong scan_spec from scanner started by cron job",
            )
            # these checks are maybe a bit redundant...
            print(
                self.output,
                "Running scanner Magenta",
                "Wrong scanner were started by cron"
            )
            print(
                len(self.output.split('\n')),
                1,
                "Wrong number of scanners were started"
            )


mag = test()
