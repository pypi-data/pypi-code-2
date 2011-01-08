#! /usr/bin/python
from ygrep.ygreplib import Ygrep

file = open('example15.yaml').read()
print Ygrep(r'\n*', color=True).do_it(file)

