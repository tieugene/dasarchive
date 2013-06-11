#!/bin/env python
# -*- coding: utf-8 -*-

import sys, re

reload(sys)
sys.setdefaultencoding('utf-8')

#TMP = re.compile('[0-9A-F]{8}')
TMP = re.compile('^bytes=(\d*)-(\d*)$')

tests = (
    'bytes=0-99',
    'bytes=100-',
    'bytes=-199',
    'bytes=1234',
    'absdf'
)

for i in tests:
    m = TMP.match(i)
    print i, m
    if (m):
        print m.groups(), '=', m.group(1), '-', m.group(2)
