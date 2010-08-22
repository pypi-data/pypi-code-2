#!/usr/bin/env python
# coding: utf-8
from __future__ import division
from packages import get_graph
import pylab
import ln

g=get_graph()

def dd():
    d=g.in_degree()
    m=max(d)
    dd=[d.count(i) for i in range(m+1)]
    return dd

dd1=dd()
dd2=[(i,dd1[i]) for i in range(len(dd1)) if dd1[i] and 0< i <30]
print dd2[-20:]

x=[i for i,j in dd2]
y=[j for i,j in dd2]
#x=x[1:]
#y=y[1:]
x2=pylab.log10(x)
y2=pylab.log10(y)
m,b=ln.linearis(x2,y2)
print m,b

pylab.loglog(dd(),"x")
pylab.hold(True)
A=10**b
pylab.loglog(x,A*x**m)
pylab.show()

