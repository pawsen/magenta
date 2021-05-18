#!/usr/bin/env python3

import cProfile
import re
cProfile.run('re.compile("foo|bar")', 'restats.out')
