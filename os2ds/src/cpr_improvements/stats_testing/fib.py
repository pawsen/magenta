#!/usr/bin/env python3


def fib(n):
    if n <= 1:
        return 1
    return fib(n - 2) + fib(n - 1)