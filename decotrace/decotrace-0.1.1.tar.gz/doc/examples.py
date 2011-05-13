#! /usr/bin/env python

from decotrace import traced

@traced
def add(a, b):
    return a + b

@traced
def recursive_geometric(n):
    if n == 0:
        return 0
    else:
        return n + recursive_geometric(n-1)

class Adder (object):
    def __init__(self, a):
        self.a = a

    @traced
    def add(self, b):
        return self.a + b

@traced
class Incrementer (int):
    def __init__(self, v=0):
        self.v = 0

    def inc(self, amt=1):
        self.v += amt
        return self.v

    classvar = 42

    def _p1(self):
        return self.classvar

    def __p2(self):
        return self.inc

    def __add__(self, other):
        return self.v + other



add(2, 3)
Adder(2).add(3)
recursive_geometric(3)
add(2, b=3)
add(a=2, b=3)
recursive_geometric(n=3)

i = Incrementer()
i.inc()
i.inc(amt=7)
