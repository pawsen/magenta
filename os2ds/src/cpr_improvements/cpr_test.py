#!/usr/bin/env python


import re
from typing import List, Match, Optional, Tuple, Union
from itertools import chain

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


    # in is faster than re https://stackoverflow.com/a/4901653
    # another way could be to make a regex based on a list of words, ie
    # r"(?:^|(?<= ))(" + "|".join(CONTEXT_WORDS) + r")(?:(?= )|$)"   OR
    # r"\b(" + "|".join(CONTEXT_WORDS) + r")\b"
    # To include support for cpr-nr and variations
    # "\b(MORE_WORDS|cpr(?::|\-)?(?:nr|nummer)?|MORE_WORDS)\b
    # "\b(MORE_WORDS|cpr[:\-]?(?:nr|nummer)?|MORE_WORDS)\b"

"""

# test string
s1 = """
2205995008: forbryder,
230500 0003: forbryder,
240501-0006: forbryder,
250501-1987: forbryder"

Hej, jeg er fra Magenta. Dette er linjen der handler om Danni Als med nr: [111111-1118].
Han bor: bordet længst tilbage, th. for tavlen og kan godt lide fodbold.

Anders (111111-1118 And) på Paradisæblevej

Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nummer: 2305000003
240501-0006. Men

### VALID CPRs
[...]16768 0 LMT} {-111111-1118 -18000 0 ACT} {-111111-1118 -14400 1 ACST} {-111111-1118 -18000 0 ACT} [...]
[...]730400 0 0 WET} {111111-1118 3600 1 WEST} {111111-1118 0 0 WET} {111111-1118 3600 1 WEST} {213762[...]
[...], "HOST/ARB08B200319.intra.coop"], "uSNChanged": [111111-1118], "uSNCreated": [662950], "userAccountControl": [[...]
"""

s2 = """

Eksempler på kontekst-tjek

@ Godtages fordi det er et valid CPR der opfylder Modulus 11 tjek.
Anders And 111111-1118
@ godtages fordi der indgår cpr i linjen
Anders And, cpr: [111111-1118
@ godtages fordi parenteser er balanceret
Anders And, [111111-1118], Paradisæblevej 111
@ godtages ikke fordi parenteser er ubalanceret.
Anders [111111-1118 And], Andeby
@ godtages fordi der tillades ekstra ord ved runde parenteser.
Anders (111111-1118 And), Andeby
@ godtages ikke fordi foranstående ord er et tal, der IKKE opfylder kriterium for CPR
Anders And 113 111111-1118
@ godtages fordi bagvedstående/foranstående ord opfylder kriterium for CPR
Anders And 111111-1118 111111-1118
@ Første CPR godtages ikke, fordi foranstående ord er en variation af .
Vejstrand Kommune, Børne- og Ungeforvaltningen. : 111111-1118, 111111-1118

@ godtages ikke fordi foranstående ord er et mix af store og små bogstaver
"HOST/ARB08B200319.intra.coop"], "uSNChanged": [111111-1118], "uSNCreated": [662950], "userAccountControl":
@ godtages ikke pga. ubalanceret parenteser
730400 0 0 WET} {111111-1118 3600 1 WEST} [111111-1118 0 0 WET] (111111-1118 3600 1 WEST) {213762
@ godtages ikke pga foranstående er unær operatør(dvs. fortegns-minus. På eng: unary) eller specialsymbol
16768 0 LMT} {-111111-1118} {+111111-1118} (#111111-1118)


Følgende kriterier undersøges
Kontekst består af de 15 foranstående/bagvedstående tegn og undersøges efter følgende heuristik, for at estimere en sandsynlighed om et 10-cifret nummer der opfylder modulus 11, rent faktisk er et CPR-nummber.

- indgår ”p:” eller variant deraf noget sted i teksten
- Er der unær operator før eller efter, fx -11111111-1118 eller 111111-1118+
- Er der ubalanceret symboler eller parenteser omkring, fx [11111111-1118 Men [11111111-1118] vil være ok.
- Kommer der et tal - der ikke ligner et CPR før eller efter, fx 113 11111111-1118
- Er ord før eller efter ikke ’alle små’-, ’stort begyndelsesbogstav’ eller ’alle caps’, fx uSNChanged 11111111-1118
resulterer alle i sandsynlighed=0.


- indeholder ord før "cpr", fx Anders CPR-nr 11111111-1118
resulterer i  sandsynlighed=1

Følgende symboler undersøges
- unær operatører "+", "-"
- parenteser "(", "[", "{", "<", "<?", "<%", "/*"
- symboler "!", "#", "%"

"""

# if the sourronding context contains some of these, we get suspicious.
# fmt: off
_p_numbers = ("p-nr.", "p.nr.", "p-nr.:", "p.nr.:", "p-nummer:", "pnr", "pnr:",)
_pre_delim = ("(", "[", "{", "<", "<?", "<%", "/*", )
_post_delim = (")", "]", "}", ">", "?>", "%>", "*/", )
_operators = ("+", "-", )
_symbols = ("!", "#", )
_all_symbols = _operators + _symbols
_pre_sym =  _operators + _symbols + _pre_delim
_post_sym =  _operators + _symbols + _post_delim
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


def is_generic_word(words: list) -> bool:
    # short-circuit or. return False if any string in the list is not alpha_case
    for s in words:
        if not is_alpha_case(s):
            return False
    return True


def is_alpha_case(s: str) -> bool:
    # Return True for Magenta, magenta, MAGENTA but not MaGenTa
    # We could enforce s.isalpha() to prevent ma10ta, but then "nr:" would fail
    s = s.replace("-","")
    return s.istitle() or s.islower() or s.isupper() and s.isalpha()


def old_examine_context(
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
    pre_list = filter(None, re.split(_split_sym, pre)) if len(pre) > 0 else [""]
    post_list = filter(None, re.split(_split_sym, post)) if len(post) > 0 else [""]

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
        print("##not in case")
        probability = 0

    return probability


def extract_surrounding_words(self, match,
                                n_words:int=5):#  -> Tuple[List[str], List[str]]:
    """Extract at most `n_words` before and after the match"""

    content = match.string
    low, high = match.span()
    pre = self._compiled_expression.sub("xxxx", content[:low])
    post = self._compiled_expression.sub("xxxx", content[high:])
    # pre_list = pre.split()[-n_words:]
    # post_list = post.split()[:n_words]
    # pre_list = pre_list if len(pre_list) else [""]
    # post_list = post_list if len(post_list) else [""]

    pre_list = list(filter(None, re.split(_split_sym, pre)))[-n_words:]
    post_list = list(filter(None, re.split(_split_sym, post)))[:n_words]

    pre_list = pre_list if len(pre_list) > 0 else [""]
    post_list = post_list if len(post_list) > 0 else [""]

    # split in two capture groups: (words, symbols)
    word_str = r"(\w+(?:[-\./]\w+)*)"
    symbol_str = r"([^\w\s\.\"])"
    split_str = r"|".join([word_str, symbol_str])
    pre_res = re.findall(split_str,pre)
    post_res = re.findall(split_str,post)
    pre_words = [s[0] for s in pre_res if s[0]][-n_words:]
    post_words = [s[0] for s in post_res if s[0]][:n_words]

    pre_sym = [s[1] for s in pre_res if s[1]][-n_words:]
    post_sym = [s[1] for s in post_res if s[1]][:n_words]

    words = dict(pre= pre_words if len(pre_words) > 0 else [""],
                 post=post_words if len(post_words) > 0 else [""])
    symbols = dict(pre= pre_sym if len(pre_sym) > 0 else [""],
                 post=post_sym if len(post_sym) > 0 else [""])
    # w = pre_words + post_words
    # s = pre_sym + post_sym
    # words = w if len(w) > 0 else [""]
    # symbols = s if len(s) > 0 else [""]

    print(" ".join(pre.split()[-n_words:]), content[low:high] , " ".join(post.split()[:n_words]))
    # pre_list = list(filter(None, re.split("(\W)", pre, flags=re.UNICODE)))[-n_words:] if len(pre) > 0 else [""]
    # post_list = list(filter(None, re.split("(\W)", post, flags=re.UNICODE)))[:n_words] if len(post) > 0 else [""]

    #return pre_list, post_list
    return words, symbols

def examine_context(self, match: Match[str]) -> Optional[int]:
    """Estimate a probality (0-1) based on the context of the match

    Returns 0 if any of the following conditions are found
    - pre-content ends with a variation of `p-nr`
    - There are unmatched delimiters, like () or {}
    - The CPR-nr is surrounded by a number that doesn't resembles a CPR
    - The word before or after is not either: lower-, title- or upper-case.

    But returns 1 if
    - pre-content contains "cpr"
    """

    probability = None

    content = match.string
    low, high = match.span()
    # print("split", content.split())
    # print("re findall1", re.findall(r"(\w+)|(\W)", content))
    # print("re findall2", re.findall(r"\w+", content))
    # print("re split1", [w for w  in filter(None,re.split(r"(\w+| )", content))]  )
    # print("re split2", [w for w in [w.strip() for w in
    #                                filter(None,re.split(r"(\w+)|[\.,: !\?\n\r]",
    #                                                            content)) ]  if w] )
    #pre, post = extract_surrounding_words(content, low, high, n_words=5)
    words, symbols = extract_surrounding_words(self, match, n_words=2)

    #print(f"context1\n{' '.join(pre + post)}")
    # remove surrounding words that resemble cpr
    #context = self._compiled_expression.sub("", " ".join(pre + post)).split()
    # words["pre"] = self._compiled_expression.sub(" ", " ".join(words["pre"])).split()
    # words["post"] = self._compiled_expression.sub(" ", " ".join(words["post"])).split()

    # context = [w for w in pre + post if not modulus11_check(w)]
    words_lower = [w.lower() for w in chain.from_iterable(words.values())]

    #print(f"words\n{' '.join(words)}")
    #print(f"symbols\n{' '.join(symbols)}")

    # import ipdb; ipdb.set_trace()
    if any(w in " ".join(words_lower) for w in self.CONTEXT_WORDS):
        print("context word")
        return 1

    delimiters = 0
    for w in chain.from_iterable(symbols.values()):
        #print(f"word {w}")
        #if any(w.rfind(s) != -1 for s in _pre_sym):
        #elif any(w.find(s) != -1 for s in _post_sym):

        # test for balanced delimiters and remove it
        if w.startswith(_pre_sym):
            delimiters += 1
            w = w[1:]
        elif w.endswith(_pre_sym):
            delimiters += 1
            w = w[:-1]
        elif w.startswith(_post_sym):
            delimiters -= 1
            w = w[1:]
        elif w.endswith(_post_sym) :
            delimiters -= 1
            w = w[:-1]

        #print(f"word {w}")
    # only do context checking on surrounding words
    #surround_words = [w for w in [pre[-1], post[0]] if w]
    #print("surrounding w", surround_words)

    for w in [words["pre"][-1], words["post"][0]]:
        print(f"@@word {w}")
        if w == '':
            continue
        elif w.endswith(_all_symbols) or w.startswith(_all_symbols):
            print(f"##is symbol {w}")
            probability = 0
        elif is_number(w):
            # test if surrounding word is a number
            print(f"##is number {w}")
            probability = 0
        elif not is_alpha_case(w):
            # test for case, ie Magenta, magenta, MAGENTA are ok, but not MaGenTa
            # nor magenta10. w must not be empty string
            print(f"##is case {w}")
            probability = 0

    if delimiters != 0:
        print(f"##{delimiters} is unbalanced {symbols}")
        probability = 0
    return probability



c = cpr_.CPRRule(modulus_11=True, ignore_irrelevant=True, examine_context=True)
content = s1
content = s2
for i, m in enumerate(c._compiled_expression.finditer(content)):
    if i > 16:
        break
    cpr = m.group(1).replace(" ", "") + m.group(2)
    low, high = m.span()
    pre = content[max(low - 15, 0) : low].rstrip()
    post = content[high : min(high + 15, len(content))].lstrip()
    # only examine content if there is any
    if c._examine_context and len(content) > 10:
        probability = 1
        context_length = 15
        # print(f"content\n{content[max(low-15,0): high+15]}")
        #p1 = old_examine_context(content, low, high, context_length)
        p = examine_context(c, m)
        probability = p if p is not None else probability
        if probability:
            print(f"###Found the CPR {cpr} at probability 1")
