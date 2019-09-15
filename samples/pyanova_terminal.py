#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2017, c3V6a2Vy <c3V6a2Vy@protonmail.com>
# This software is under the terms of Apache License v2 or later.


"""REPL Demo with pyanova

"""
import re
from pyanova import pyanova
from __future__ import print_function

if __name__ == '__main__':
    print('~~ pyanova demo ~~')
    print('-- Initializing PyAnova object')
    pa = pyanova.PyAnova(debug=True)
    cmd_re = re.compile('^get|^stop|^set')
    cmd_list = list(filter(lambda m: cmd_re.match(m), dir(pa)))
    print('-- PyAnova object initialized')
    print('-- Available commands:\n    %s'%'\n    '.join(cmd_list))
    print('-- Type commands like: \'get_current_temperature()\' or \'set_temperature(42)\'')
    print('-- Type \'bye\' to end demo')
    while True:
        ri = raw_input('> ')
        if ri.lower().startswith('bye'):
            print('cya.')
            break
        else:
            print('< ' + eval('pa.'+ri))
