#!/usr/bin/env python3
from datetime import date
import csv
from os2datascanner.engine2.rules.utilities import cpr_probability

"""Calculate all possible CPRs for a given date and save the result to a CSV
file"""

cpr = cpr_probability.CprProbabilityCalculator()

# each new list of calculated cprs (approx 545 but limited to 10) is appended to
# cprs as a new row.
cprs = []
for y in range(1980, 1981):
    for m in range(1, 13):
        for d in range(1, 32):
            try:
                bdate = date(day=d, month=m, year=y)
                cprs.append(cpr._calc_all_cprs(birth_date=bdate)[:10])
            except ValueError as e:
                print(f"{e}, {y}-{m}-{d}")


# format the cprs a bit nicer
cprs2 = [[f"{x[:6]}-{x[6:]}" for x in row] for row in cprs]

# opening the file object with @newline="" prevents file() from terminating new
# lines. csw.writer terminates lines on its own.

#This should prevent the file from having \r\n as line endings. CR+LF or ^M, the
# newline character in windows. Unix only uses \n (LF, Line Feed).
# But it seems not to work.
# https://docs.python.org/3/library/csv.html#id3
with open("cprs.csv", "w", newline="") as fp:
    writer = csv.writer(fp, delimiter=",")
    # writer.writerow(["day", "header", "foo"])  # write header
    writer.writerows(cprs2)

    # swap cols and rows when writing to file
    # writer.writerows(zip(*cprs2))
