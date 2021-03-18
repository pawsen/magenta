#!/usr/bin/env python

import os
import os.path
import http.server
from datetime import datetime
import contextlib
from multiprocessing import Manager, Process
import socket

from os2datascanner.engine2.model.core import (Handle,
        Source, SourceManager, UnknownSchemeError)
from os2datascanner.engine2.model.http import (
        WebSource, WebHandle, make_outlinks)
from os2datascanner.engine2.model.utilities.datetime import parse_datetime
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.conversions.utilities.results import SingleResult

from start_server import start_server_if_not_running

"""
Modified from
https://git.magenta.dk/os2datascanner/os2datascanner/-/blob/development/src/os2datascanner/engine2/tests/test_engine2_http.py
"""

here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data")

site = WebSource("http://localhost:64346/")
mapped_site = WebSource("http://localhost:64346/",
        sitemap="http://localhost:64346/sitemap.xml")


ws = start_server_if_not_running()

def test_exploration():
    count = 0
    with SourceManager() as sm:
        for h in site.handles(sm):
            count += 1
            print(h.relative_path)
    print(f"Embedded site should have 3 handles. Have {count}")

def test_exploration_sitemap():
    count = 0
    with SourceManager() as sm:
        for h in mapped_site.handles(sm):
            count += 1
            print(h.relative_path)
            if h.relative_path == "hemmeligheder2.html":
                lm = h.follow(sm).get_last_modified().value
                print('modification date', lm.year, lm.month, lm.day)
    print(f"embedded site with sitemap should have 5 handles. Have {count}")

def test_resource():
    with SourceManager() as sm:
        first_thing = None
        with contextlib.closing(site.handles(sm)) as handles:
            first_thing = next(handles)
        r = first_thing.follow(sm)
        print(
            f"{first_thing}: *last modification date* is not a SingleResult\n"
            f"{repr(r)}, {repr(SingleResult)}, {r.get_last_modified()}\n"
            f"{first_thing}: *last modification date value()* is not a datetime.datetime\n"
            f"{repr(r)}, {repr(datetime)}, {r.get_last_modified().value}\n"
            )
        with r.make_stream() as fp:
            stream_raw = fp.read()
        with r.make_path() as p:
            with open(p, "rb") as fp:
                file_raw = fp.read()
        print(f'stream_raw\n{stream_raw}')
        print(f'file_raw\n{file_raw}')
