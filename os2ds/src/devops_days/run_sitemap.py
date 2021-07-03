#!/usr/bin/env python3

from os2datascanner.engine2.model.core import (Handle,
        Source, SourceManager, UnknownSchemeError)
from os2datascanner.engine2.model.http import (
        WebSource, WebHandle, make_outlinks)

url = "http://135.181.86.32:8000"
url = "http://localhost:8000"
site = WebSource(url,
        sitemap=f"{url}/sitemap_passwd.xml")
        # sitemap=f"{url}/sitemap.xml")

def test_resource():
    with SourceManager() as sm:
        # with contextlib.closing(mapped_site.handles(sm)) as handles:
        for h in site.handles(sm):
            print(h.presentation)
            r = h.follow(sm)
            try:
                with r.make_stream() as fp:
                    stream_raw = fp.read()
                    #print(stream_raw)
            except:
                print("url not found")

if __name__ == "__main__":
    test_resource()
