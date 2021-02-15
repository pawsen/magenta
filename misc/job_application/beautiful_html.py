#!/usr/bin/env python3

"""Cleanup version of
https://github.com/os2datascanner/os2datascanner/blob/master/src/os2datascanner/engine2/conversions/text/html.py
"""

from bs4 import BeautifulSoup
from bs4.element import Tag


def _unwrap_node(n, top=False):
    if isinstance(n, Tag):
        for child in n.children:
            _unwrap_node(child)
        n.smooth()
        if not top:
            n.unwrap()


def html_processor(html, **kwargs):
    """BS4_parser"""
    soup = BeautifulSoup(html, "lxml")
    if soup.body:
        _unwrap_node(soup.body, top=True)
        return " ".join(soup.body.get_text().split())  #, soup.body.get_text()
    else:
        return None
