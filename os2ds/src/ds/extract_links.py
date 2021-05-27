#!/usr/bin/env python3

from pprint import pprint

from os2datascanner.engine2.model.core import (Handle,
        Source, SourceManager, UnknownSchemeError)
from os2datascanner.engine2.model.http import (
        WebSource, WebHandle, make_outlinks)
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions import registry
from os2datascanner.engine2.rules.links_follow import LinksFollowRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.pipeline import messages

""" Run the `LinksFollowRule` converter on a webpage and then the rule on the
conveted content.

"""

converters = registry.__converters
# pprint(f"converters {converters}")

sm = SourceManager()
site = WebSource("http://localhost:64346/")
page = WebHandle(source=site, path="side.html")

resource = page.follow(sm)
resource.check()
mime_type = resource.compute_type()
print(f"mime_type of resource {mime_type}")
link_list = convert(resource, OutputType.Links).value


rule = LinksFollowRule(sensitivity=Sensitivity.INFORMATION)
matches = list(rule.match(link_list))
msg = messages.MatchFragment(rule, matches or [])
