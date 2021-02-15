#!/usr/bin/env python3
#
import os
import os.path
import timeit
from copy import deepcopy

from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import html
from os2datascanner.engine2.conversions.registry import conversion
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.model.core import Handle, Source, SourceManager
from os2datascanner.engine2.model.file import (FilesystemHandle,
                                               FilesystemResource,
                                               FilesystemSource)
from os2datascanner.engine2.pipeline import messages, processor
from os2datascanner.engine2.rules.regex import RegexRule


## subclass FilesystemSource to specify mime-type
# BS4
class bs4FilesystemSource(FilesystemSource):
    type_label = "bs4"

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return FilesystemSource(path=obj["path"])


class bs4FilesystemResource(FilesystemResource):
    def compute_type(self):
        return "text/bs4html"


@Handle.stock_json_handler("bs4")
class bs4FilesystemHandle(FilesystemHandle):
    type_label = "bs4"
    resource_type = bs4FilesystemResource


# LXML
class lxmlFilesystemSource(FilesystemSource):
    type_label = "lxml"

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return FilesystemSource(path=obj["path"])


class lxmlFilesystemResource(FilesystemResource):
    def compute_type(self):
        return "text/lxmlhtml"


@Handle.stock_json_handler("lxml")
class lxmlFilesystemHandle(FilesystemHandle):
    type_label = "lxml"
    resource_type = lxmlFilesystemResource


## Conversions
# BS4
def _unwrap_node(n, top=False):
    if isinstance(n, Tag):
        for child in n.children:
            _unwrap_node(child)
        n.smooth()
        if not top:
            n.unwrap()


@conversion(OutputType.Text, "text/bs4html")
def bs4_html_processor(r, **kwargs):
    with r.make_stream() as fp:
        soup = BeautifulSoup(fp, "lxml")
        if soup.body:
            _unwrap_node(soup.body, top=True)
            return " ".join(soup.body.get_text().split())
        else:
            return None


# lxml
@conversion(OutputType.Text, "text/lxmlhtml")
def html_processor(r, **kwargs):
    with r.make_stream() as fp:
        try:
            return html.parse(fp).xpath("//body")[0].text_content()
        except AssertionError:
            return None


curdir = os.path.dirname(__file__)
benchpath = os.path.join(curdir, "..", "..", "data", "html_benchmark", "data")
benchpath = os.path.abspath(benchpath)

# BS4: create json to inject into the conversion queue
bs4_obj = messages.ConversionMessage(
    scan_spec=messages.ScanSpecMessage(
        scan_tag="dummy",
        source=bs4FilesystemSource(benchpath),
        rule=RegexRule("[Aa]rachnid"),
        configuration={},
        progress=None,
    ),
    handle=bs4FilesystemHandle(bs4FilesystemSource(benchpath), "html.html"),
    progress=messages.ProgressFragment(rule=RegexRule("[Aa]rachnid"), matches=[]),
).to_json_object()


lxml_obj = deepcopy(bs4_obj)
lxml_obj["scan_spec"]["source"]["type"] = "lxml"
lxml_obj["handle"]["type"] = "lxml"
lxml_obj["handle"]["source"]["type"] = "lxml"


def test_conversion_html(obj):
    return list(
        processor.message_received_raw(obj, "os2ds_conversions", SourceManager())
    )


## timing
# no conversion on my computer takes 0.00049414.
print(f"## timing")
t = timeit.Timer(lambda: test_conversion_html(bs4_obj))
print(f"bs4:\t{t.timeit(number=5):.5}")

t = timeit.Timer(lambda: test_conversion_html(lxml_obj))
print(f"lxml:\t{t.timeit(number=5):.5}")

"""
| no conv |   bs4 |  lxml |
|---------+-------+-------|
| 0.00049 | 0.992 | 0.043 |
"""


## compare output word-by-word using wdiff -3 $file1 $file2 | colordiff
SAVE = True


def save_output(obj, fname):
    obj = test_conversion_html(obj)
    msg = obj[0][1]
    text = msg["representations"]["text"]

    os.makedirs(os.path.join(curdir, "out"), exist_ok=True)
    fpath = os.path.join(curdir, "out", f"{fname}_html.txt")
    print(f"## dumping to file {os.path.basename(fpath)}")
    with open(fpath, "w") as fp:
        fp.write(text)

    return obj, text


if SAVE:
    save_output(bs4_obj, "bs4")
    save_output(lxml_obj, "lxml")
