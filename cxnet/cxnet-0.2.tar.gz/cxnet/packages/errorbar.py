#!/usr/bin/env python
# coding: utf-8
from __future__ import division

import pylab

def errorbar():
    x = pylab.linspace(0.1,2,11)
    y = x**-1.3
    xerr = 0.2
    pylab.errorbar(x,y,xerr=[[0.2]*11, [0.1]*11], fmt=" k")
    pylab.gca().set_yscale("log")
    pylab.gca().set_xscale("log")
    pylab.show()

if __name__ == "__main__":
    errorbar()
