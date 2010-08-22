#!/usr/bin/env python
# coding: utf-8
from __future__ import division

import packages 
from pylab import *
import ln

def degree_distribution():
 G=packages.get_graph()
 deg=G.in_degree()
 print len(deg), "A csúcsok száma"
 m=max(deg); print m, "A legnagyobb fokszám"
 dd=[(i, deg.count(i)) for i in range (m+1)]
 return dd
dd=degree_distribution()
print dd[:20]
print dd[-20:]

def kirajzol(dd):
 x=[i for i,j in dd]
 y=[j for i,j in dd]
 loglog (x,y,".")
 show()
kirajzol(dd)

def illeszt(dd,min=None,max=None):
 x=[i for i,j in dd[min:max] if j!=0]
 y=[j for i,j in dd[min:max] if j!=0]
 lgx=log10(x)
 lgy=log10(y)
 k, lgA=ln.linearis(lgx,lgy)
 print k,lgA
illeszt(dd,1,100)