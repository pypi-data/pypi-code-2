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
dd2=[(i,dd1[i]) for i in range(len(dd1)) if dd1[i]] # and 0< i <30]
print dd2[-20:]

x=[i for i,j in dd2]
y=[j for i,j in dd2]
s=sum(y)
p= [i/s for i in y]
#x=x[1:]
#y=y[1:]
x2=pylab.log10(x)
y2=pylab.log10(y)
m,b=ln.linearis(x2,y2)
print m,b

#def elso_hiany(x):
#    for i in range(len(x)):
#	if x[i+1] - x[i] > 1:
#	    return i+1
#
#e=elso_hiany(x)
#print zip(x,y)[e-1: e+30]
#
#print zip(x,y)[:20]
#print zip(x,y)[-20:]

def intervallum_hatarok(x):
    ih=[]
    for i in range(len(x)-1):
	ih.append(pylab.sqrt(x[i]*x[i+1]))
    ih.append(x[-1]**2/ih[-1])
    return ih

print intervallum_hatarok(x)

#pylab.loglog(dd(),"x")
pylab.hold(True)
A=10**b
#pylab.loglog(x,A*x**m)
#pylab.show()


