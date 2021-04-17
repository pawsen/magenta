#!/usr/bin/env python3

import json
import time
from uuid import uuid4

import io
import gzip

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.explorer import (
        message_received_raw as explorer_mrr)
from os2datascanner.engine2.pipeline.worker import (
        message_received_raw as worker_mrr)
from os2datascanner.engine2.pipeline.exporter import (
        message_received_raw as exporter_mrr)

from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions.types import OutputType, encode_dict
from os2datascanner.engine2.model.derived.filtered import GzipSource
import requests

"""
url = "http://www.syddjurs.dk/sitemap_aaben_indsigt.xml.gz"
r = requests.get(url)
mime = r.headers["content-type"]
cont = r.content
"""

def _get_top(s: Source) -> Source:
    while s.handle:
        s = s.handle.source
    return s

body = {
    "rule":{
        "type": "regex",
        "expression": "[Tt]est"},
    "source": {
        "type": "data",
        "content": "VGhpcyBpcyBvbmx5IGEgdGVzdA==",
        "mime": "text/plain",
        "name": "test.txt"}
    }


source = Source.from_json_object(body["source"])
top_type = _get_top(source).type_label

rule = Rule.from_json_object(body["rule"])

message = messages.ScanSpecMessage(
        scan_tag=messages.ScanTagFragment(
                time=time_now(),
                user=None,
                scanner=messages.ScannerFragment(
                        pk=0,
                        name="API server demand scan"),
                organisation=messages.OrganisationFragment(
                        name="API server",
                        uuid=uuid4())),
        source=source,
        rule=rule,
        configuration={},
        progress=None).to_json_object()

with SourceManager() as sm:
    for c1, m1 in explorer_mrr(message, "os2ds_scan_specs", sm):
        if c1 in ("os2ds_conversions",):
            for c2, m2 in worker_mrr(m1, c1, sm):
                if c2 in ("os2ds_matches",
                        "os2ds_metadata", "os2ds_problems",):
                    print(m3 for _, m3 in exporter_mrr(m2, c2, sm))
        elif c1 in ("os2ds_problems",):
            print(m2 for _, m2 in exporter_mrr(m1, c1, sm))
