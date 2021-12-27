#!/usr/bin/env python3

import logging

from os2datascanner.engine2.model.http import *
from os2datascanner.engine2.model.core import SourceManager

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("os2datascanner")
logger.setLevel(logging.DEBUG)

ws = WebSource("http://www.localhost:64345/undermappe", sitemap="")
ws = WebSource(
    "http://www.localhost:64345/undermappe",
    sitemap="http://localhost:64345/sitemap_subpage.xml",
)

with SourceManager() as sm:
    for i, h in enumerate(ws.handles(sm)):
        print(f"{h.presentation_url}")
        if i > 100:
            break

if nurlsdasdsadsa.hostname == url_splitdadsa.hostname and nurlsdadsafdsfdsd.path.startswith(
    url_split.path
):
    pass
