#!/usr/bin/env python3

import json
import io
import gzip
import base64

from os2datascanner.engine2.model.core import Source, SourceManager, Handle, Resource
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.model.derived.filtered import GzipSource, FilteredHandle
from os2datascanner.engine2.model.data import DataHandle, DataSource

## XXX something is wromng here. Not same output as from cli
def gzip_str(s: str) -> bytes:
    #out = io.BytesIO()
    with io.BytesIO() as out, gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(s.encode())
        return out.getvalue()

def gunzip_bytes(b: bytes) -> str:
    return gzip.decompress(b).decode()

def b64encode(b: bytes) -> bytes:
    return base64.b64encode(b)

#  "application/x-gzip" not defined
mime = "application/gzip"
s_str = "Hello world"
b64_content = b64encode(s_str.encode())
gzip_content_pyt1 = gzip_str(s_str)
gzip_content_pyt2 = gzip.compress(s_str.encode())
print("are the two byte representation of the gzipped strings equal? ",
      gzip_content_pyt1 == gzip_content_pyt2)

# But this is not the same as what I get from cli... why...
# echo "Hello world - gzip" | gzip | base64 -w0
b64_str = b"H4sIAAAAAAAAA/NIzcnJVyjPL8pJUdBVSK/KLOACANzsSzgTAAAA"
gzip_content = base64.decodebytes(b64_str)

sm = SourceManager()

# registrered types:
"""
Source._json_handlers
# used in Source.from_json_object(obj)
#  obj["type"]

decorator:
Source.__mime_handlers
# used for containers. Source.from_handle(h) uses
# mime = h.guess_type() or mime = h.compute_type()

decorator: Source.url_handler
Source.__url_handlers
# used in Source.from_url(url), uses
# scheme = url.split(:)
"""

# gzip source json needs a handle(as all other derived Sources)
# can we supply raw byte content?
json_gzip = {
    "type": "filtered-gzip",
    "content": gzip_content,
    "mime":  "application/gzip",
    "name": "test.txt",
    "handle": {
        "type": "filtered",
        "source": "",
    }
}

json_data = {
    "type": "data",
    "content": b64_content,
    "mime": "text/plain",
    "name": "test.txt",
}

# json `data` content needs to be base64 encoded
json_gzip = {
    "type": "data",
    "content": b64encode(gzip_content),
    "mime":  "application/gzip",
    "name": "test.txt",
}



for j in (json_data, json_gzip,):
    s = Source.from_json_object(j)
    while True:
        h_generator = s.handles(sm)
        h = next(h_generator)
        r = h.follow(sm)

        #if h.guess_type() == "text/plain":
        print(f"handle\t{h}")
        print(f"resource\t{r}")

        print("raw content:")
        with r.make_stream() as fp:
            print("\t\t{0}".format(fp.read()))

        # should succed for text -> text conversion
        try:
            rep = convert(r, OutputType.Text)
            print(f"Conveted\t{rep.value}")
            break
        except KeyError as e:
            # lets try to reinterpret the handle as a new Source
            s = Source.from_handle(h)


# sz = Source.from_handle(h)
# hz = next(sz.handles(sm))
# rz = hz.follow(sm)
# with rz.make_stream() as fp:
#     print("\t\t{0}".format(fp.read()))


## Lets try manual
hd = DataHandle(DataSource(content=b64encode(gzip_content), mime="text/plain",
                           name="sitemap.xml.gz"),
                relpath="sitemap.xml.gz"
                )
rd = hd.follow(sm)
print("data resource b64encoded gzip -  ")
with rd.make_stream() as fp:
    print("\t\t{0}".format(fp.read()))
## QUESTION: How do I b64decode with engine



## Non-b64encoded data
hd = DataHandle(DataSource(content=(gzip_content), mime="application/gzip",
                           name="sitemap.xml.gz"),
                relpath="sitemap.xml.gz"
                )
rd = hd.follow(sm)
print("data resource gzip - ")
with rd.make_stream() as fp:
    print("\t\t{0}".format(fp.read()))

hgz = FilteredHandle(GzipSource(hd), "sitemap.xml")
rgz = hgz.follow(sm)

print("data resource gzip - Filtered gzip")
with rgz.make_stream() as fp:
    print("\t\t{0}".format(fp.read()))
