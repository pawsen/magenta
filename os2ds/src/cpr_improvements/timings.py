#!/usr/bin/env python

from random import choice
from decorators import timing
from string import ascii_lowercase, digits

# generate random list of strings
chars = ascii_lowercase + digits
context = [''.join(choice(chars) for _ in range(12)) for _ in range(1000)]
whitelist  = [''.join(choice(chars) for _ in range(12)) for _ in range(1000)]
context.append(whitelist[-1] + "partial")
print(context[-1])

@timing
def f1(n):
    for cw in whitelist:
        res = next(
            (True for keyword in context if cw in keyword),
            False,
        )
        if res:
            print(cw)
            return 1
    print("word not found")
    return 0

@timing
def f2(n):
    for cw in whitelist:
        res = next(
            (True for keyword in context if cw in keyword),
            False,
        )
        if res:
            print(cw)
            return 1
    print("word not found")
    return 0


@timing
def f3(n):
    for cw in whitelist:
        if cw in context:
            print(cw)
            return 1
    print("word not found")
    return 0


@timing
def f4(n):
    for cw in whitelist:
        for keyword in context:
            if cw in keyword:
                print(cw)
                return 1
    print("word not found")
    return 0


f1(1)
#f2(2)
f3(3)
f4(3)
