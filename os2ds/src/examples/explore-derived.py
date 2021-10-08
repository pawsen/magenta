#!/usr/bin/env python3

import sys
from pathlib import Path
from os2datascanner.engine2.model.file import FilesystemSource, FilesystemHandle
from os2datascanner.engine2.model.derived.zip import ZipHandle, ZipSource
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.model.core import FileResource, Handle, Source
from os2datascanner.engine2.model.data import DataSource, DataHandle
from os2datascanner.engine2.model.core import (
    Source,
    Handle,
    SourceManager,
    UnknownSchemeError,
    DeserialisationError,
)

datadir = Path().resolve().parent / "data/derived"
fwd = datadir

sm = SourceManager()

def try_apply(source, sm, rule=None):
    print(f"try_apply got called with source {source.type_label}")

    for handle in source.handles(sm):
        derived = Source.from_handle(handle, sm)

        print(
            f"type:\t{handle.source.type_label}\n"
            f"\thandle           \t{handle.presentation}\n"
            f"\tname             \t{handle.name}\n"
            f"\tsort_key         \t{handle.sort_key}\n"
            f"\tpresentation_name\t{handle.presentation_name}\n"
        )

        if derived:
            yield from try_apply(derived, sm, rule)
        else:
            # import ipdb; ipdb.set_trace()

            resource = handle.follow(sm)
            operates_on = rule.operates_on if rule else OutputType.Text
            representation = convert(resource, operates_on)
            print(representation.value)
            if representation and rule:
                yield from rule.match(representation.value)


rule = None
def run_on_handle(handle):
    with SourceManager() as sm:
        source = Source.from_handle(handle, sm)
        matches = list(try_apply(source, sm, rule))


fname = "embedded-cpr.pdf"
fname = "embedded-cpr.odt"
fname = "embedded-cpr.docx"
fname = "embedded-cpr-odt.zip"
fname = "embedded-cpr-pdf.zip"
fname = "embedded-cpr.eml"
handle = FilesystemHandle.make_handle(fwd / fname)

run_on_handle(handle)

# testfile = FilesystemHandle(FilesystemSource(fwd), "test.txt")

# fs = FilesystemSource(fwd)
# fh = FilesystemHandle(fs, "cpr-test-single.zip")
# zs = ZipSource(fh)
# zh = ZipHandle(zs,"cpr-test-single.txt")

# zsm = ZipSource(FilesystemHandle(FilesystemSource(fwd), "cpr-test-multiple.zip"))
# zhm1 = ZipHandle(zsm, "cpr-test/cpr-test2.zip")
# zhm2 = ZipHandle(zsm, "cpr-test/cpr-test3.zip")

# zsmd1 = ZipSource(zhm1)
# zhmd1 = ZipHandle(zsmd1, "cpr2-test.txt")

# sm = SourceManager()
# rz_list = []
# count = 0
# with SourceManager() as sm:
#     for h in zsm.handles(sm):
#         handle = h
#         rz = h.follow(sm)
#         rz_list.append(rz)
#         print(h)
#         print(
#             f"type:\t{handle.source.type_label}\n"
#             f"\thandle  \t{handle.presentation}\n"
#             f"\tsort_key\t{handle.sort_key}\n"
#             f"\tname    \t{handle.name}\n"
#                     )

#         count += 1

# print(f"handles found {count}")

# def contains(self, h) -> bool:
#     while h:
#         if h.source == self:
#             return True
#         elif h.source.handle:
#             print(f"previous handle\n{h}")
#             h = h.source.handle
#             print(f"new handle\n{h}")
#         else:
#             break
#     return False

# print(f"source: {zsm}, handle: {zh}.\nSource contains handle: {contains(zsm, zh)}")
# print(f"source: {fs}, handle: {zh}.\nSource contains handle: {contains(fs, zh)}")
# print(f"source: {fs}, handle: {zhm1}.\nSource contains handle: {contains(fs, zhm1)}")

# s =  zhmd1.source
# while s.handle:
#     print(s)
#     s = s.handle.source
# print(s)
