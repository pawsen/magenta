#!/usr/bin/env python3

from typing import Match, Tuple, Dict, cast, TypeVar, Callable, Any
import re

def extract_surrounding_words_all(
    self, match: Match[str], n_words: int = 2
) -> Tuple[Dict[str, list], Dict[str, list]]:
    """Extract at most `n_words` before and after the match

    Return a dict with words and one with symbols
    """

    # get full content
    content = match.string
    low, high = match.span()
    # replace what look like cpr's with something that does not interfere
    # with the logic of examine_context
    pre = self._compiled_expression.sub("xxxx", content[max(low-50,0):low])
    post = self._compiled_expression.sub("xxxx", content[high:high+50])
    # get previous/next n words
    pre = " ".join(pre.split()[-n_words:])
    post = " ".join(post.split()[:n_words])

    # split in two capture groups: (word, symbol)
    # Ex: 'The brown, fox' ->
    # [('The', ''), ('brown', ''), ('', ','), ('fox', '')]
    word_str = r"(\w+(?:[-\./]\w*)*)"
    symbol_str = r"([^\w\s\.\"])"
    split_str = r"|".join([word_str, symbol_str])
    pre_res = re.findall(split_str, pre)
    post_res = re.findall(split_str, post)
    # remove empty strings
    pre_words = [s[0] for s in pre_res if s[0]]
    post_words = [s[0] for s in post_res if s[0]]
    pre_sym = [s[1] for s in pre_res if s[1]]
    post_sym = [s[1] for s in post_res if s[1]]

    # XXX Should be set instead?
    words = dict(
        pre=pre_words if len(pre_words) > 0 else [""],
        post=post_words if len(post_words) > 0 else [""],
    )
    symbols = dict(
        pre=pre_sym if len(pre_sym) > 0 else [""],
        post=post_sym if len(post_sym) > 0 else [""],
    )
    return words, symbols

def extract_surrounding_words_fixed(
    self, match: Match[str], n_words: int = 2
) -> Tuple[Dict[str, list], Dict[str, list]]:
    """Extract at most `n_words` before and after the match

    Return a dict with words and one with symbols
    """

    # get full content
    content = match.string
    low, high = match.span()
    # replace what look like cpr's with something that does not interfere
    # with the logic of examine_context
    pre = content[max(low-50,0):low]
    post = content[high:high+50]
    # get previous/next n words
    pre = " ".join(pre.split()[-n_words:])
    post = " ".join(post.split()[:n_words])

    # split in two capture groups: (word, symbol)
    # Ex: 'The brown, fox' ->
    # [('The', ''), ('brown', ''), ('', ','), ('fox', '')]
    word_str = r"(\w+(?:[-\./]\w*)*)"
    symbol_str = r"([^\w\s\.\"])"
    split_str = r"|".join([word_str, symbol_str])
    pre_res = re.findall(split_str, pre)
    post_res = re.findall(split_str, post)
    # remove empty strings
    pre_words = [s[0] for s in pre_res if s[0]]
    post_words = [s[0] for s in post_res if s[0]]
    pre_sym = [s[1] for s in pre_res if s[1]]
    post_sym = [s[1] for s in post_res if s[1]]

    # XXX Should be set instead?
    words = dict(
        pre=pre_words if len(pre_words) > 0 else [""],
        post=post_words if len(post_words) > 0 else [""],
    )
    symbols = dict(
        pre=pre_sym if len(pre_sym) > 0 else [""],
        post=post_sym if len(post_sym) > 0 else [""],
    )
    return words, symbols

