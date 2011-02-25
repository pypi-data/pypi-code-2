#!/usr/bin/env python
from __future__ import print_function # Python 2.6
from qvikconfig import parse, dump
from os.path import dirname, join

path = lambda relpath: join(dirname(__file__), relpath)
header = lambda message: message + '\n' + len(message) * '-'

print(header('Input'))
x = open(path('test1.config')).read()
print(x + '\n')

print(header('Internal dict'))
x = parse(data=x)
for key, val in sorted(x.items()):
    print({key: val})
print()

print(header('Output'))
x = dump(x)
print(x + '\n')

print(header('New internal dict'))
x = parse(data=x)
for key, val in sorted(x.items()):
    print({key: val})
print()
