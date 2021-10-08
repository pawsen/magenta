#!/usr/bin/env python3

from os2datascanner.engine2.rules.utilities.cpr_probability import *

"""Fra sag https://redmine.magenta-aps.dk/issues/46120

Får vi flg. fejlbesked
File "/code/src/os2datascanner/engine2/rules/utilities/cpr_probability.py", line 227, in cpr_check
  index_number = legal_cprs.index(cpr)
ValueError: '0101643066' is not in list

"""

cpr = "0101643066"

date = get_birth_date(cpr)
mod_check = modulus11_check(cpr)

calculator = CprProbabilityCalculator()

prob = calculator.cpr_check(cpr, do_mod11_check=True)
prob = calculator.cpr_check(cpr, do_mod11_check=False)

day = int(cpr[0:2])
month = int(cpr[2:4])
year = int(cpr[4:6])

year_check = int(cpr[6])

print(mod_check)
