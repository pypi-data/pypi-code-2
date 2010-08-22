#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import pylab
import networkx as nx
import sys
sys.path.insert(0, "..")
from properties.degdist import DegreeDistribution, power_law_fitting
from time import localtime, time, strftime
hms = lambda : ".".join("%02d" % i for i in localtime()[:3]) + " " +  ":".join("%2.2d" % i for i in localtime()[3:6])
from random import random

def exponent(values):
    values = pylab.array(values)
    minimum = min(values)
    summa = sum(pylab.log(values/minimum))
    n = len(values)
    alpha = 1 + n/summa
    sigma = pylab.sqrt(n) / summa
    return alpha, sigma


def try_barabasi_albert():
    for i in range(20):
        print i
        print hms()
        G = nx.barabasi_albert_graph(100000, 3)
        print hms()
        degrees = G.degree()
        max_deg = max(degrees)
        exponent(degrees)

        xy_values = [(i, degrees.count(i)) for i in xrange(max_deg+1) ] 
        print "alpha (all): %f (A: %f)" % power_law_fitting(xy_values)

        DD = DegreeDistribution(G)
        DD.exponent()

def generate_power_law(n=100000, alpha=3, xmin=1):
    """Generate Pareto distribution."""
    values = [ xmin*(1-random())**(-1/(alpha-1)) for i in xrange(n) ]
    return values

def largest_values(n=50):
    """Returns with the exponent and the largest value of a sample."""
    largest_values = []
    for i in xrange(n):
        values = generate_power_law()
        alpha, sigma = exponent(values)
        maximum = max(values)
        print "alpha:   %f +- %f, maximum: %15.10f" % (alpha, sigma, maximum)
        largest_values.append(maximum)
    return largest_values

if __name__  == "__main__":
    lv = largest_values()
    print "Maximum and minimum of largest values:\n%9.2f %9.2f" % (max(lv), min(lv))
    print "%9.7f +- %9.7f is the exponent of the largest values." % exponent(lv)

