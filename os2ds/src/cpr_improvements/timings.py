#!/usr/bin/env python

from random import choice
from decorators import timing
from string import ascii_lowercase, digits

"""generate two list of random strings. Append last word from
whitelist+'parital' to context.
Then time how long it takes to find that last word from whitelist in context,
and even if it is found, as the metch is a substring.

In this test, the generator (f1) is not faster than the explicit two for-loops(f3).
"""
chars = ascii_lowercase + digits
context = [''.join(choice(chars) for _ in range(12)) for _ in range(1000)]
whitelist  = [''.join(choice(chars) for _ in range(12)) for _ in range(1000)]
context.append(whitelist[-1] + "partial")
print(context[-1])


##
@timing
def f1(n):
    """Use a iterator
    This give a match, when 'abc' in 'abcdef'"""
    for cw in whitelist:
        res = next(
            (True for keyword in context if cw in keyword),
            False,
        )
        if res:
            print(cw)
            return 1
    print("word NOT found")
    return 0


@timing
def f2(n):
    """One for-loop, checking if a word is in the other list
    This does not give a match, when 'abc' in 'abcdef'"""
    for cw in whitelist:
        if cw in context:
            print(cw)
            return 1
    print("word NOT found")
    return 0


@timing
def f3(n):
    """two for-loops, checking each word
    This give a match, when 'abc' in 'abcdef'"""
    for cw in whitelist:
        for keyword in context:
            if cw in keyword:
                print(cw)
                return 1
    print("word not found")
    return 0


f1(1)
f2(2)
f3(3)
