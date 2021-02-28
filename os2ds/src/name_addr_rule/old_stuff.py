#!/usr/bin/env python3


import os.path

curdir = os.path.dirname(__file__)
benchpath = os.path.join(curdir, "..", "..", "data", "input-text.txt")
fpath = os.path.abspath(benchpath)

with open(fpath, 'r') as f:
    text_buffer = f.read()


# maybe optimized
simple_name = r"\p{Lu}(\p{L}+)"
name = r"{0}(-{0})?".format(simple_name)
full_name_regex2 = regex.compile(
    r"\b(?P<first>" + name + r")" +
    r"(?P<middle>(" + _whitespace + name + r"){0,3})" +
    r"(?P<last>" + _whitespace + name + r"){1}\b", regex.UNICODE)



def test_regex(regex, data):
    matches = regex.findall(data)
    return matches


import timeit
print(f"## timing")
t = timeit.Timer(lambda: test_regex(full_name_regex, text_buffer))
print(f"regex:\t{t.timeit(number=5):.5}")
t = timeit.Timer(lambda: test_regex(full_name_regex2, text_buffer))
print(f"regex:\t{t.timeit(number=5):.5}")
