#!/usr/bin/env python3

import pstats
from pstats import SortKey

"""List of `sort_stat` keys
https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats

"""


# p = pstats.Stats('restats.out')
#p.sort_stats(-1).print_stats()
# The strip_dirs() method removed the extraneous path from all the module names.
#p.strip_dirs().sort_stats(-1).print_stats()

p = pstats.Stats('res.out')
p.sort_stats(SortKey.CUMULATIVE).print_stats(10)
p.sort_stats(SortKey.PCALLS).print_stats(10)
p.sort_stats(SortKey.TIME).print_stats(10)

# sorts statistics with a primary key of time, and a secondary key of cumulative
# time, and then prints out some of the statistics. To be specific, the list is
# first culled down to 50% (re: .5) of its original size, then only lines
# containing init are maintained, and that sub-sub-list is printed.
p.sort_stats(SortKey.TIME, SortKey.CUMULATIVE).print_stats(.5, 'init')
# get a list of callers for each of the listed functions.
# p.print_callers(.5, 'init')

p.print_stats('cpr', .1)
p.print_stats('cpr')
