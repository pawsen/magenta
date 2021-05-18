#!/usr/bin/env python3


from fib import fib
import pytest

"""
pip install
pip install pytest-benchmark[histogram]


# generate data
pytest bench.py --benchmark-json output.json
pytest bench.py --benchmark-autosave

# compare runs
pytest-benchmark list
pytest-benchmark compare

pytest bench.py --benchmark-autosave --benchmark-histogram

https://pytest-benchmark.readthedocs.io/en/stable/comparing.html
"""

def test_fib_10(benchmark):
    benchmark(fib, 10)

def test_fib_20(benchmark):
    benchmark(fib, 20)
