#!/usr/bin/env python3

import sys
from pathlib import Path
from os2datascanner.engine2.model.file import FilesystemSource, FilesystemHandle
from os2datascanner.engine2.model.derived.zip import ZipHandle, ZipSource
from os2datascanner.engine2.model.core import FileResource, Handle, Source
from os2datascanner.engine2.model.data import DataSource, DataHandle
from os2datascanner.engine2.model.core import (
    Source,
    Handle,
    SourceManager,
    UnknownSchemeError,
    DeserialisationError,
)

# are we running from console? Then set __file__
try:
    __file__
except:
    __file__ = str(Path("./derived.py").resolve())

datadir = (Path(__file__).parents[1] / "data/files").resolve()
fwd = datadir.absolute()

testfile = FilesystemHandle(FilesystemSource(fwd), "test.txt")

fs = FilesystemSource(fwd)
fh = FilesystemHandle(fs, "cpr-test-single.zip")
zs = ZipSource(fh)
zh = ZipHandle(zs,"cpr-test-single.txt")

zsm = ZipSource(FilesystemHandle(FilesystemSource(fwd), "cpr-test-multiple.zip"))
zhm1 = ZipHandle(zsm, "cpr-test/cpr-test2.zip")
zhm2 = ZipHandle(zsm, "cpr-test/cpr-test3.zip")

zsmd1 = ZipSource(zhm1)
zhmd1 = ZipHandle(zsmd1, "cpr2-test.txt")

sm = SourceManager()
rz_list = []
count = 0
with SourceManager() as sm:
    for h in zsm.handles(sm):
        rz = h.follow(sm)
        rz_list.append(rz)
        print(h)
        count += 1

print(f"handles found {count}")

def contains(self, h) -> bool:
    while h:
        if h.source == self:
            return True
        elif h.source.handle:
            print(f"previous handle\n{h}")
            h = h.source.handle
            print(f"new handle\n{h}")
        else:
            break
    return False

print(f"source: {zsm}, handle: {zh}.\nSource contains handle: {contains(zsm, zh)}")
print(f"source: {fs}, handle: {zh}.\nSource contains handle: {contains(fs, zh)}")
print(f"source: {fs}, handle: {zhm1}.\nSource contains handle: {contains(fs, zhm1)}")

s =  zhmd1.source
while s.handle:
    print(s)
    s = s.handle.source
print(s)
