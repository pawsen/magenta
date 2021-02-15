#!/usr/bin/env python3

import timeit, functools
from unittest import TestCase as tc

import requests
import html2text
from lxml import html
from io import StringIO

from beautiful_html import html_processor as bs_html_processor
from simple_html import html_parser as simp_html_processor


def html2text_ex(content):
    """html2text"""
    h = html2text.HTML2Text()
    # Ignore converting links from HTML
    h.ignore_links = True
    page = h.handle(content)
    return page


def lxml_ex(content):
    """lxml"""
    # This tells lxml to retrieve the page, locate the <body> tag then extract
    # and print all the text.
    body = html.parse(StringIO(content)).xpath("//body")[0].text_content()
    return body


def loadfile(fname):
    with open(fname, "r") as f:
        return f.read()


def test_func(first, second):
    """assertEqual method expects the first argument to be an object reference.
    Circumvent by using dummy object"""
    dummy_obj = tc()
    tc.assertEqual(dummy_obj, first, second, msg="Not Equal")


SIMPLE_HTML = (
    "This is only a test. "
    "There's one paragraph, "
    "and then there's the other paragraph."
)


# sha1 of master, 20200112
SHA1 = "588f921a56a4fc4ab29e3a714a61941879ef6e30"

base_url = (
    f"https://raw.githubusercontent.com/os2datascanner/os2datascanner/{SHA1}/src/"
    f"os2datascanner/engine2/tests/data/html/"
)
pages = ["simple.html"]
correct_html = [SIMPLE_HTML]

html_processors = [bs_html_processor, simp_html_processor, lxml_ex, html2text_ex]

fname = "simple.html"
html_content = loadfile(fname)


def run_test(html_processor):
    for page, correct in zip(pages, correct_html):
        # url = base_url + page
        # resp = requests.get(url)
        # html_content = resp.content

        body = html_processor(html_content)
        # format lxml's output in the same way BS4 is formatted
        if html_processor.__doc__ == "lxml":
            body = " ".join(body.split())
        try:
            test_func(body, SIMPLE_HTML)
            print(f"{html_processor.__doc__:20}; passed test for {page}")
        except AssertionError as e:
            print(f"{html_processor.__doc__:20}; failed test for {page}\n{e}")
        finally:
            return body


for parser in html_processors:
    run_test(parser)
# bs_body = run_test(bs_html_processor)
# simp_body = run_test(simp_html_processor)


# Test with another random page from the internet
# https://github.com/html5lib/html5lib-python/tree/master/benchmarks/data
fname = "html.html"
html_content = loadfile(fname)


def run_test2(parser):
    body = parser(html_content)
    return body


malbody = []
for parser in html_processors:
    malbody.append(run_test2(parser))

try:
    test_func(malbody[0], malbody[1])
    print(f"For {fname}")
    print(f" Both parsers (BS4 & simple) returns same (malformatted) content")
except AssertionError as e:
    print(e)


print("timing:")
for parser in html_processors:
    t = timeit.Timer(functools.partial(parser, html_content))
    print(f"{parser.__doc__:20}; {t.timeit(5):.5}")
