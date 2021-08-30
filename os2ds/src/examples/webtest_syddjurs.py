#!/usr/bin/env python3

"""Vedr. https://redmine.magenta-aps.dk/issues/44585

"""

import logging
from pprint import pformat
from os2datascanner.engine2.model.http import *
from os2datascanner.engine2.model.core import SourceManager

# do initial setup for root logger, before setting the level
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
sm = SourceManager()

url = "https://www.syddjurs.dk"
page = "os2web/service/gf/v1/c5c68012-4ad5-eb11-8d7e-00505699b6b8"


h = WebHandle(WebSource(url), page)
ret = h.follow(sm).check()
print(ret)

# ws = WebSource(url)
# with SourceManager() as sm:
#     for i, h in enumerate(ws.handles(sm)):
#         print(f"{h.presentation_url}")
#         if i > 100:
#             break
