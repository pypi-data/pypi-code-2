#! /usr/bin/env python
'''
Created on Jul 29, 2010

@author: dwmclary
'''
import numpy
from scipy import stats
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

def main():
    n_sample = 100
    l=0.3
    numpy.random.seed(87655678)
    x = stats.norm.rvs(loc=l, size=n_sample)
    print "mu:"+str(numpy.mean(x))
    print "var:"+str(numpy.var(x))
    print "x:"+",".join(map(str, x.tolist()))

if __name__ == '__main__':
    main()