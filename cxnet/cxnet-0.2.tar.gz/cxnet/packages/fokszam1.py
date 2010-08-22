#!/usr/bin/env python
# coding: utf-8
from __future__ import division

import packages 
import pylab
import lknegyzetek

G=packages.get_graph()

def degree_distribution(graph):
    """A fokszámeloszlást adja vissza.
    
    A visszatérési érték párok listája.
    A párok első eleme a fokszám,
    második eleme az akkora fokszámú csúcsok száma.
    """

    deg=graph.in_degree()
    m=max(deg)
    print "A legnagyobb fokszám", m
    dd=[(i, deg.count(i)) for i in range (m+1)]
    return dd

dd=degree_distribution(G)

print dd[:20]
print dd[-20:]

def kirajzol(dd):
    x=[i for i,j in dd]
    y=[j for i,j in dd]
    pylab.loglog (x,y,".")
    pylab.show()

kirajzol(dd)

def illeszt(dd,min=None,max=None):
    x=[i for i,j in dd[min:max] if j!=0]
    y=[j for i,j in dd[min:max] if j!=0]
    lgx=pylab.log10(x)
    lgy=pylab.log10(y)
    k, lgA=lknegyzetek.linearis(lgx,lgy)
    print k,lgA

illeszt(dd,1,100)
