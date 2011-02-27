#!/usr/bin/env python

import libxml2dom.svg

d = libxml2dom.svg.createSVGDocument()
de = d.documentElement

# Test easy matrices.

m = de.createSVGMatrixComponents(2, 0, 0, 2, 0, 0)
de.setMatrixTrait("transform", m)
print de.getAttribute("transform")
m2 = de.getMatrixTrait("transform")
print "Same matrix?", m == m2
m = de.createSVGMatrixComponents(1, 0, 0, 1, 10, -10)
de.setMatrixTrait("transform", m)
print de.getAttribute("transform")
m2 = de.getMatrixTrait("transform")
print "Same matrix?", m == m2

# Test other operations.

de.setAttribute("transform", "rotate(90)")
m = de.getMatrixTrait("transform")
de.setMatrixTrait("transform", m)
print de.getAttribute("transform")
m2 = de.getMatrixTrait("transform")
print "Same matrix?", m == m2

# vim: tabstop=4 expandtab shiftwidth=4
