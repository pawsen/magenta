#!/usr/bin/env python


import re
import regex
from typing import Union
from os2datascanner.engine2.rules import cpr as cpr_

from os2datascanner.engine2.rules.cpr import modulus11_check


"""Examine content

Følgende kriterier undersøges
- Er det forrige ord p-nr: eller variant deraf
- Er der unary operator før eller efter, fx -11111111-1118
- Er der ubalanceret symboler eller delimiters omkring, fx [11111111-1118
  Men [11111111-1118] vil være ok.
- Kommer der et tal - der ikke ligner et CPR før eller efter, fx
  120 11111111-1118
- Er ord før eller efter ikke enten (alle små, stort begyndelsesbogstav eller
  alle caps), fx uSNChanged 11111111-1118
giver alle probability=0.

- indeholder ord før "cpr", fx Dannis CPR-nr 11111111-1118
giver probability=1

Se listen af `delimiters`, `symboler`, `operators` herunder.
- unary operators
  "+", "-"
- delimiters
  "(", "[", "{", "<", "<?", "<%", "/*"
- symboler
  "!", "#"

`_split_sym` er de symboler tekst-strengen splittes på. Bemærk de slettes og
indgår ikke i den splittede liste.

"""

# test string
s1 = """Hej, jeg er fra Magenta. Dette er linjen der handler om Danni Als med nr: [111111-1118].
Han bor: bordet længst tilbage, th. for tavlen og kan godt lide fodbold.

Anders (111111-1118 And) på Paradisæblevej

Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nummer: 2305000003
240501-0006. Men

### VALID CPRs
[...]16768 0 LMT} {-111111-1118 -18000 0 ACT} {-111111-1118 -14400 1 ACST} {-111111-1118 -18000 0 ACT} [...]
[...]730400 0 0 WET} {111111-1118 3600 1 WEST} {111111-1118 0 0 WET} {111111-1118 3600 1 WEST} {213762[...]
[...], "HOST/ARB08B200319.intra.coop"], "uSNChanged": [111111-1118], "uSNCreated": [662950], "userAccountControl": [[...]
"""


# if the sourronding context contains some of these, we get suspicious.
# fmt: off
_p_numbers = ("p-nr.", "p.nr.", "p-nr.:", "p.nr.:", "p-nummer:", "pnr", "pnr:",)
_pre_delim = ("(", "[", "{", "<", "<?", "<%", "/*", )
_post_delim = (")", "]", "}", ">", "?>", "%>", "*/", )
_operators = ("+", "-", )
_symbols = ("!", "#", )
_pre_sym = _pre_delim + _operators + _symbols
_post_sym = _post_delim + _operators + _symbols
_split_sym = r"[\.,: !\?\n\r]"
# fmt: on



def is_number(s: str) -> bool:
    # Not the pretties nor fastest way to do this
    if modulus11_check(s):
        return False
    try:
        float(s)
    except ValueError:
        return False
    return True


def is_generic_word(words: list)->bool:
    # short-circuit or. return False if any string in the list is not alpha_case
    for s in words:
        if not is_alpha_case(s):
            return False
    return True

def is_alpha_case(s: str) -> bool:
    # Return True for Magenta, magenta, MAGENTA but not MaGenTa
    # We could enforce s.isalpha() to prevent ma10ta, but then "nr:" would fail
    return s.istitle() or s.islower() or s.isupper() and s.isalpha()


def examine_context(
    content: str, low: int, high: int, context_length: int = 15
) -> Union[None, int]:
    """Examine the context around a potential CPR number

    Returns 0 if any of the following conditions are found
    - pre ends with p-nr
    - There are unmatched delimiters, like () or {}
    - The CPR-nr is sourrounded by a number
    - The word before or after is not either: lower-, title- or upper-case.

    But returns 1 if
    - pre contains "cpr"
    """

    probability = None
    pre = content[max(low - context_length, 0) : low].rstrip()
    post = content[high : min(high + context_length, len(content))].lstrip()

    if len(pre) == 0 and len(post) == 0:
        return probability

    # remove matching sourrounding symbols
    if pre.endswith(_pre_sym) and post.startswith(_post_sym):
        pre = pre[:-1]
        post = post[1:]
    elif pre.rfind("(") and post.find(")"):
        pre = pre.replace("(", "")
        post = post.replace(")", "")

    # pre_list = pre.split() if len(pre) > 0 else [""]
    # post_list = post.split() if len(post) > 0 else [""]
    # split and use filter to remove the empty strings returned by re.split
    pre_list = filter(None,re.split(_split_sym, pre)) if len(pre) > 0 else [""]
    post_list = filter(None,re.split(_split_sym, post)) if len(post) > 0 else [""]

    # delete all parts that could be a cpr-number
    # XXX: only do this on strings that actually looks like a cpr?
    # pre_list[:] =  # if pre_list is a list
    pre_list = [s for s in pre_list if not modulus11_check(s)]
    post_list = [s for s in post_list if not modulus11_check(s)]
    # if modulus11_check(post_list[0]):
    #     del post_list[0]

    surround_words = [s for s in [pre_list[-1], post_list[0]] if s]
    print("sourround_words", surround_words)
    print("pre_list", pre_list)
    print("post_list", post_list)

    if pre.lower().rfind("cpr") != -1:
        probability = 1
    # Filter out the most incredibly obvious P-numbers
    elif pre.lower().endswith(_p_numbers):
        print("##ends with pnr")
        probability = 0
    # test for ubalanced delimiters, union operators and symbols
    elif (pre.endswith(_pre_sym) and not post.startswith(_post_sym)) or (
        not pre.startswith(_pre_sym) and post.endswith(_post_sym)
    ):
        print("##unbalanced ")
        probability = 0
    # test if what comes before or after is a number
    # XXX this is maybe not a good idea. Does a pre number really disqualify?
    elif is_number(pre_list[-1]) or is_number(post_list[0]):
        print("##just a number")
        probability = 0

    # test for case, ie Magenta, magenta, MAGENTA are ok, but not MaGenTa
    elif not is_generic_word(surround_words):
        print("##not in case" )
        probability = 0

    return probability



c = cpr_.CPRRule(modulus_11=True, ignore_irrelevant=True, examine_context=True)
content = s1
for i,m in enumerate(c._compiled_expression.finditer(content)):
    if i > 2:
        break
    cpr = m.group(1).replace(" ", "") + m.group(2)
    low, high = m.span()
    pre = content[max(low - 15, 0) : low].rstrip()
    post = content[high : min(high + 15, len(content))].lstrip()
    # only examine content if there is any
    if c._examine_context and len(content) > 10:
        probability = 1
        context_length = 15
        print(f"content\n{content[max(low-15,0): high+15]}")
        p = examine_context(content, low, high, context_length)
        probability = p if p is not None else probability
        if probability:
            print(f"###Found the CPR {cpr} at probability 1")
