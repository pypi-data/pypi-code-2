#!/usr/bin/env python
# coding: utf-8
from __future__ import division

import packages 
import pylab
import lknegyzetek

G=packages.get_graph()

def degree_distribution(graph, bin_smearing=True):
    """A fokszámeloszlást adja vissza.
    
    Kimenet:
      Párok listája.
      A párok első eleme a fokszám,
      második eleme az akkora fokszámú csúcsok száma.

    Bemenet:
      graph: a vizsgált gráf
      csak_pozitiv: Ha igaz, csak a loglog skálán
        ábrázolható pontokat adja vissza.
    """

    deg=graph.in_degree()
    m=max(deg)
    print "A legnagyobb fokszám", m
    dd=[(i, deg.count(i)) for i in range(m+1)]
    print "A nulla fokszámú elemek száma:", dd[0]

    dd=[(i, j) for i, j in dd if i > 0 and j > 0]

    csucsok_szama = graph.number_of_nodes()
    dd=[(i, j/csucsok_szama) for i, j in dd]
    print dd[-2:]

    if bin_smearing:
	osztopontok = [pylab.sqrt(dd[i][0]*dd[i+1][0])  for i in range(len(dd)-1)]
	dd = [(dd[i][0], dd[i][1]/(osztopontok[1]-osztopontok[0]))  for i in range(1,len(dd)-1)]

    return dd

dd=degree_distribution(G)

print dd[:20]
print dd[-20:]

def kirajzol(dd, intervallumok):
    """Kirajzolja a fokszámeloszlást az illesztésekkel együtt.

    Bemenet:
      dd: fokszámeloszlás
      intervallumok: (min, max) párok listája
        az illesztések min és max-1 között történnek.
    """

    x=[i for i,j in dd]
    y=[j for i,j in dd]
    pylab.loglog (x,y,".")
    pylab.hold(True)
    for min, max in intervallumok:
	k, A = illeszt(dd, min, max)
	x = pylab.arange(min, max)
	pylab.loglog(x, A*x**k)
    pylab.show()

def illeszt(dd,min=None,max=None):
    """Hatványfüggvénnyel közelíti a fokszámeloszlást.

    A hatványfüggvény alakja y=A*x^k.

    Bemenet:
      dd: fokszámeloszlás
      min, max: min és max-1 között illeszt
    """

    x=[i for i,j in dd[min:max] if j!=0]
    y=[j for i,j in dd[min:max] if j!=0]
    lgx=pylab.log10(x)
    lgy=pylab.log10(y)
    k, lgA=lknegyzetek.linearis(lgx,lgy)
    return k, 10**lgA

kirajzol(dd, [(1,100), (100, 10000)])
