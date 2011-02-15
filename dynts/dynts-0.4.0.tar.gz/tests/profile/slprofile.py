#!/usr/bin/env python
# encoding: utf-8
# filename: slprofile.py
from _base import *
from dynts.lib import skiplist

from random import random


MAXSIZE = 100000

data = populate(MAXSIZE)


def insert():
    sl = skiplist(MAXSIZE)
    for d in data:
        sl.insert(d)


def run():
    cProfile.runctx("insert()",
                    globals(),
                    locals(),
                    "Profile.prof")

