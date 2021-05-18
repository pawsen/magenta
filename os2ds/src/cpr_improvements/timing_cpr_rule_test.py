#!/usr/bin/env python3

from pathlib import Path
import logging

from old_cpr_rule import CPRRule as CPROld
from simpler_cpr_rule import CPRRule as CPRSimple
from complicated_cpr_rule import CPRRule as CPRComplicated
from cpr_functions import(
    extract_surrounding_words_all, extract_surrounding_words_fixed,
)

from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.rules.cpr import CPRRule, modulus11_check
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions.types import OutputType

from typing import Match, Tuple, Dict, cast, TypeVar, Callable, Any
from copy import deepcopy
import re
from functools import wraps
from time import time
from types import MethodType
import re
#from faker import Faker
#
logging.basicConfig(level=logging.ERROR)
logging.getLogger(__name__).setLevel(logging.DEBUG)

#logging.basicConfig(level=logging.DEBUG)

F = TypeVar('F', bound=Callable[..., Any])
def timing(func: F) -> F:
    """@timing decorator
    """
    @wraps(func)
    def wrap(*args, **kw):
        ts = time() * 1000
        result = func(*args, **kw)
        te = time() * 1000
        print('func:{!r}, took: {:.4f} ms'.format(
          func.__name__, te-ts ))
        return result
    return cast(F, wrap)

def try_apply(sm, source):
    for handle in source.handles(sm):
        derived = Source.from_handle(handle, sm)
        if derived:
            try_apply(sm, derived)
        else:
            resource = handle.follow(sm)
            representation = convert(resource, OutputType.Text)
            return representation.value

def get_content_from_handle(handle):
    with SourceManager() as sm:
        source = Source.from_handle(handle, sm)
        assert source is not None, f"{handle} cound not be made into a Source"
        return try_apply(sm, source)


try:
    cwd = Path(__file__).parent.absolute()
except:
    cwd = Path().absolute()
fpath = cwd / '../data/files/document.docx'
#fpath = cwd / '../data/files/cpr-examples.odt'

reload_content = True
reload_content = False
try:
    content
except:
    reload_content = True

if reload_content:
    h = FilesystemHandle.make_handle(fpath)
    content = get_content_from_handle(h)




# newrule = CPRRule(modulus_11=True, ignore_irrelevant=False,
#                   examine_context=True)
# newrule.extract_surrounding_words = MethodType(extract_surrounding_words_fixed, newrule)

rules = [

    (CPRSimple(modulus_11=True, ignore_irrelevant=False, examine_context=True),
     "simple w. context"),
#    (CPRComplicated(modulus_11=True, ignore_irrelevant=False, examine_context=True),
#     "'accepted' w. context"),
#    (CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True),
#     "current w. context"),
#    # (CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True),
#    #  "current w. context"),
#    (CPROld(modulus_11=True, ignore_irrelevant=False,
#                 examine_context=False),
#     "old wo. context"),
#    (CPROld(modulus_11=True, ignore_irrelevant=False,
#                 examine_context=True),
#     "old w. context"),
    # (newrule, "new w. context"),
]

for rule, description in rules:

    print(description)
    @timing
    def f(rule):
        ret = list(rule.match(content))
        return ret

    ret = f(rule)
    print(len(ret))


# @timing
# def regex_replace_full_context():
#     newrule = deepcopy(rule)
#     res = run_rule_on_handle(h, newrule)
#     return list(res)


# @timing
# def fixed_context():
#     newrule = deepcopy(rule)
#     newrule.extract_surrounding_words = MethodType(extract_surrounding_words_fixed, newrule)

#     res = run_rule_on_handle(h, newrule)
#     return list(res)

# @timing
# def old_rule():
#     res = run_rule_on_handle(h, oldrule)
#     return list(res)

# res1 = regex_replace_full_context()
# res2 = fixed_context()
# res3 = old_rule()
