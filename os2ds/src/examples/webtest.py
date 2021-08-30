#!/usr/bin/env python3

import logging
from pprint import pformat
from urllib.parse import *
from os2datascanner.engine2.model.http import *
from os2datascanner.engine2.model.core import SourceManager


# do initial setup for root logger, before setting the level
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
sm = SourceManager()

"""
As of MR
https://git.magenta.dk/os2datascanner/os2datascanner/-/merge_requests/579, it
should not matter if the url ends with '/' or not.

However
"http://www.magenta.dk"
"https://magenta.dk"
does not work, as DS doesn't allow for redirects

Get the final url after redirects, https://stackoverflow.com/a/3077316
curl -Ls -I -o /dev/null -w %{url_effective} http://magenta.dk
"""
url = "https://www.magenta.dk"
url = "http://localhost:64346"
sitemap = urljoin(url, "sitemap_underside.xml")
ws = WebSource(url, sitemap,
               exclude=[urljoin(url, "undermappe"), urljoin(url, "kontakt.html")])
with SourceManager() as sm:
    for i, h in enumerate(ws.handles(sm)):
        print(f"{h.presentation_url}")
        if i > 100:
            break
