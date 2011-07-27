#!/usr/bin/env python
import random
from KDTree import KDTree

testsize = 20000
numneighbors = 1
pt = (random.random(), random.random())
pts= [(random.random(), random.random()) for i in xrange(testsize)]

t = KDTree(pts)
print "Root:", t.root.point
print "Tree size:", t.num_nodes()
print "Nearest %d Neighbor(s) to %s: %s" % (numneighbors, pt, t.nearest_neighbors(pt, n=numneighbors))

