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
    __file__ = str(Path(".").resolve())

datadir = Path(__file__) / "data" / "files"

testfile = FilesystemHandle(FilesystemSource(datadir.absolute()), "test.txt")
testzip = ZipHandle(
    ZipSource(
        FilesystemHandle(FilesystemSource(datadir.absolute()), "simple.zip")),
    "test.txt",
)

sm = SourceManager()

rfile = testfile.follow(sm)
rzip = testfile.follow(sm)
