#!/usr/bin/env python3

from pathlib import Path
from inspect import getsourcefile
from pprint import pformat

from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.model.derived.libreoffice import LibreOfficeSource
from os2datascanner.engine2.rules.cpr import CPRRule
import os2datascanner.engine2.conversions as C

# are we running from console? Then set __file__
try:
    __file__
except:
    __file__ = Path(getsourcefile(lambda:0)).resolve()
datadir = (Path(__file__).resolve().parent.parent / "data/derived").absolute()
fpath = datadir / "ex1.ods"

rule = CPRRule(modulus_11=False, ignore_irrelevant=False)

sm = SourceManager()
lrfs = LibreOfficeSource(FilesystemHandle(FilesystemSource(datadir), "ex1.ods"))
lrfh = list(lrfs.handles(sm))[0]
lrfr = lrfh.follow(sm)

#representation = C.convert(lrfr, C.types.OutputType.Text).value
representation = C.convert(lrfr, rule.operates_on).value

# matches = list( rule.match(representation))
# print(pformat(matches))



"""
# get source from a file-handle pointing to the file.
# get the "correct" handle from the source
# folow the handle to get the resource, ie. content of the file
lrfs = Source.from_handle(FilesystemHandle.make_handle(fpath))
lrfh = list(lrfs.handles(sm))[0]
lrfr =lrfh.follow(sm)
"""
