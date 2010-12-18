#!/usr/bin/python

import os
import sys
import doctest
import sqlite3
from contextlib import closing

import babel

DB_SCHEMA = '../../demo/sql/model/schema.sql'
DB_FILE = '../../demo/sql/model/db.sqlite'
def init_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    with closing(sqlite3.connect(DB_FILE)) as db:
        with open(DB_SCHEMA, 'r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()
init_db()


os.environ['LANG'] = 'C'
os.environ['LANG'] = 'en_US.utf8'
doctest.ELLIPSIS = 10

files = (
    'completions.txt',
    'dates.txt',
    'defaults.txt',
    'django2sa.txt',
    'fields.txt',
    'filters.txt',
    'mapper_inspect.txt',
    'mask.txt',
    )

if sys.argv[1:]:
    files = sys.argv[1:]

for filename in files:
    print filename
    os.environ['LANG'] = 'en_US.utf8'
    doctest.testfile(filename, optionflags=doctest.ELLIPSIS)

    

