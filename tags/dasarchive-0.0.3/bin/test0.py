#!/bin/env python
# -*- coding: utf-8 -*-
'''
testdav.py - tool to test WebDAV servers: make right and wrong requests - and saves responces.
./testdav.py http://localhost:8000/dav/ test
python testdav.py http://localhost/dasarchive/dav/ test
'''
# 1. system
import os, sys, pprint

# 2. 3rd parties
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

# 1. get currents
current = dict()
db = MySQLdb.connect(host="localhost",
    user="dasarchive",
    passwd="dasarchive",
    db="dasarchive")
cur = db.cursor()
cur.execute("SELECT id, fname, md5 FROM dasarchive_file ORDER BY id")
for row in cur.fetchall() :
    current[row[0]] = (row[1], row[2])
db.close()
