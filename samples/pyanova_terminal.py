#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2017, c3V6a2Vy <c3V6a2Vy@protonmail.com>
# This software is under the terms of Apache License v2 or later.


"""REPL Demo with pyanova

"""
from __future__ import print_function
import re
from pyanova import pyanova

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

    # for python2/3 compatibility
    try: input = raw_input
    except NameError: pass

    while True:
        ri = input('> ')
        if ri.lower().startswith('bye'):
            print('cya.')
            break
        else:
            try:
                print('< ' + eval('pa.'+ri))
            except:
                print('< failed to execute command: ' + ri + ', make sure command is a valid method with proper arguments.')
