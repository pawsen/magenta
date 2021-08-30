#!/usr/bin/env python3

import inspect
from urllib.parse import urlsplit, urlparse, urljoin, urlunsplit, ParseResult, scheme_chars
import re
import tldextract

"""Terminologi

uri: Uniform Resource Identifiers
url: Uniform Resource Locator
urn: Uniform Resource Name

URL refers to the subset of URI that identify resources via a representation of
their primary access mechanism (e.g., their network "location"), rather than
identifying the resource by name

URN refers to the subset of URI that are required to remain globally unique and
persistent even when the resource ceases to exist or becomes unavailable

scheme://netloc/path;parameters?query#fragment

Example of a full URL
http://user:pwd@magenta.dk:80/path;param?query=arg#frag

See this page for many examples of parsing URI
https://pymotw.com/3/urllib.parse/index.html

The suffix
TLD: Top Level Domain
gTLD: generic top-level domain
ccTLD: country code top-level domain

The core group of generic top-level domains consists of the (com, info, net, and
org) domains.

The (.cn, .tk, .de and .uk) ccTLDs contain the highest number of domains.

See this module, which splits netloc, tld, etc
https://github.com/john-kurkowski/tldextract/blob/master/tldextract/tldextract.py#L215

Notes:
https://tools.ietf.org/html/rfc3986#section-3
"""


# scheme://netloc/path;parameters?query#fragment
url1 = f"https://sub.magenta.dk/"
url2 = f"https://sub.magenta.dk/underside"
url3 = f"https://magenta.dk/path;parameters?info=true#nr3"
full_url = 'http://user:pwd@magenta.dk:80/path;param?query=arg#frag'

urls = (url1, url2, url3, full_url)
print()
for url in urls:
    print(urlsplit(url))
    print(urlparse(url))

o = urlsplit(url3)
parsed = urlparse(full_url)
print('scheme  :', parsed.scheme)
print('netloc  :', parsed.netloc)
print('path    :', parsed.path)
print('params  :', parsed.params)
print('query   :', parsed.query)
print('fragment:', parsed.fragment)
print('username:', parsed.username)
print('password:', parsed.password)
print('hostname:', parsed.hostname)
print('port    :', parsed.port)

# exclude dunder __ and private _
members = [m for m in dir(parsed) if not m.startswith(('_',))]
print(f"all public methods and attributes of a ParsedResult instance\n {members}")
# same, but as a list of (name, value) pairs
[print(m) for m in inspect.getmembers(parsed) if not m[0].startswith("_")] # and not inspect.ismethod(m[1])



##
lst = list(["*.magenta.dk/", "sub.magenta.dk/", "magenta.dk/s", "last.magenta.dk/q"])
lst = [u if u.startswith("http") else "http://" + u for u in lst ]
for url in lst:
    if not url.startswith("http"):
        url = "https://" + url
    parsed = urlsplit(url)
    print(f"netloc: {parsed.netloc}\thostname: {parsed.hostname}\tpath: {parsed.path}")
    ext = tldextract.extract(url)
    print((ext.subdomain, ext.domain, ext.suffix))

labels = parsed.netloc.split(".")
subdomain = ".".join(labels[:-1])
# regex for finding the netloc
SCHEME_RE = re.compile(r'^([' + scheme_chars + ']+:)?//')
netloc = (
            SCHEME_RE.sub("", lst[-1])
            .partition("/")[0]
            .partition("?")[0]
            .partition("#")[0]
            .split("@")[-1]
            .partition(":")[0]
            .strip()
            .rstrip(".")
        )

ext = tldextract.extract('http://forums.bbc.co.uk')

# @staticmethod
# def _exclude_strip_scheme(exclude):
#     for ex in exclude:
#         urlsplit(ex)._rep

exclude = ["https://labs.magenta.dk", "magenta.dk/q"]
exs = [urlunsplit(urlsplit(ex)._replace(scheme="")).lstrip("//") for ex in exclude]
print(exs)
