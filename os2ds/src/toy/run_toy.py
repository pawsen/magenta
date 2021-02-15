#!/usr/bin/env python3

from toy import *
from os2datascanner.engine2.model.core import SourceManager
import magic  # for determining mime type
import os

sm = SourceManager()
source = ToySource(username="alec", password="secretpassword")

paths = [h.relative_path for h in source.handles(sm)]
print(paths)

# determine file type from magic bytes
mime = magic.Magic(mime=True)

# Then we can print more information about these files:
for h in source.handles(sm):
    print(h.relative_path)
    fname = os.path.basename(h.relative_path)
    r = h.follow(sm)
    print("\tSize: {0} bytes".format(r.get_size()))
    if h.guess_type() == "text/plain":
        print("\tContent:")
        with r.make_stream() as fp:
            print("\t\t{0}".format(fp.read().decode()))

    with r.make_stream() as fp:
        content = fp.read()
        # same as r.compute_type() implemented in FileResource
        # we could only read the first 512 bytes to get mime type
        mtype = mime.from_buffer(content)
        with open(fname, 'wb') as fh:
            fh.write(content)


# To see how the pipeline can work with data sources of all kinds without
# knowing what they are, we can try working with the JSON form of ToySource:
from os2datascanner.engine2.model.core import Source, SourceManager

sm = SourceManager()
generic_source = Source.from_json_object({
        "type": "toy", "username": "alec",
        "password": "secretpassword"})
print([h.relative_path for h in generic_source.handles(sm)])



""" The description of Handles earlier glossed them as references to "objects".
But what is an object?

To some extent this depends on the Source. In a filesystem, an object is a file:
a named stream of bytes with some metadata. In an email account, an object is an
email. In a case management system, an object is a case.

But sometimes the lines are blurrier than that. For example, consider a Zip
file. It is a file: it's a stream of bytes with a name, a size, and some
metadata. It can also, however, be viewed as a container for other files, each
of which in turn also has these properties.

Let's put one into the toy filesystem and see what happens.
"""

backing_store["alec:secretpassword"]["/home/alec/hello.zip"] = {
    "type": "application/zip",
    "content": b"PK\x03\x04\x14\x00\x00\x00\x08\x00a~\xbdP4\x01\xd3p@"
               b"\x00\x00\x00C\x00\x00\x00\t\x00\x1c\x00hello.txtUT\t"
               b"\x00\x03E\x13\xd1^c\x12\xd1^ux\x0b\x00\x01\x04\xe8"
               b"\x03\x00\x00\x04\xe8\x03\x00\x00\xf3H\xcd\xc9\xc9\xd7"
               b"Q(\xcf/\xcaIQ\xe4\n\xc9\xc8,V\x00\xa2\xfc\xbc\x9cJ"
               b"\xaeD\x85\x92\xd4\xe2\x12=\xa0`jQ*H4/\x9f+/55E\xa1$_!"
               b")\x95+1'\xb1(75E\x8f\x0b\x00PK\x01\x02\x1e\x03\x14"
               b"\x00\x00\x00\x08\x00a~\xbdP4\x01\xd3p@\x00\x00\x00C"
               b"\x00\x00\x00\t\x00\x18\x00\x00\x00\x00\x00\x01\x00"
               b"\x00\x00\xa4\x81\x00\x00\x00\x00hello.txtUT\x05\x00"
               b"\x03E\x13\xd1^ux\x0b\x00\x01\x04\xe8\x03\x00\x00\x04"
               b"\xe8\x03\x00\x00PK\x05\x06\x00\x00\x00\x00\x01\x00"
               b"\x01\x00O\x00\x00\x00\x83\x00\x00\x00\x00\x00"
}


# ToyResource doesn't expose a lot of operations, but it does return a Python
# file object pointing at the content of the Zip file. As luck would have it,
# the Python standard library has a module for working with Zip files:
h2 = ToyHandle(
        ToySource(
                username="alec",
                password="secretpassword"),
        "/home/alec/hello.zip")



# ToyResource doesn't expose a lot of operations, but it does return a Python
# file object pointing at the content of the Zip file. As luck would have it,
# the Python standard library has a module for working with Zip files:
from zipfile import ZipFile

r2 = h2.follow(sm)
with r2.make_stream() as fp:
    print(ZipFile(fp).infolist())


"""Is there a way of exploring this Zip file from inside engine2? If, for
example, the pipeline is asked to look for the text illegal, and it finds a Zip
file, then text conversion won't work -- the result would be binary gibberish.
But shouldn't there be some way to recurse into the Zip file and look at the
things inside it?

There is:
"""
from os2datascanner.engine2.model.derived.zip import ZipSource

print([h.relative_path for h in ZipSource(h2).handles(sm)])

zs = ZipSource(h2)
print(zs.to_json_object())

zs2 = Source.from_json_object(zs.to_json_object())
print(zs == zs2)
print([h.relative_path for h in zs2.handles(sm)])
