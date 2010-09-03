#!/util/bin/python

import numpy
from numpy import median

from mpgutils import utils

maxiter = 10
eps = 0.01


def npmedian (x):
    """Dear numPY.  Please don't change your APIs, so I don't have to wrap them."""
    nv=numpy.__version__
    
    if (nv =="1.0.1" or nv =="1.0.4" or nv=="1.1" or nv =="1.1.1"): 
        return median(x)
    
    return median(x, axis=0)

# Takes a ndarray and returns the median polish total, row strengths, column strengths, and residues
# Converted from the R version into python
def medpolish(x):
    z = x.copy()

    nrows,ncols = z.shape

    t = 0
    r = numpy.zeros(nrows,dtype='f')
    c = numpy.zeros(ncols,dtype='f')
    oldsum = 0
    converged = 0
    
    for iter in range(1,maxiter + 1):
        rdelta = npmedian(z.transpose())
        r = r + rdelta
        rdelta.shape = (nrows,1)
        z = z - utils.repmat(rdelta,1,ncols)

        delta = npmedian(c)
        c = c - delta
        t = t + delta
        
        cdelta = npmedian(z)
        c = c + cdelta
        cdelta.shape = (1,ncols)
        z = z - utils.repmat(cdelta,nrows,1)

        delta = npmedian(r)
        r = r - delta
        t = t + delta

        newsum = sum(sum(abs(z)))
        if (newsum == 0) or (abs(newsum - oldsum) < eps * newsum):
            converged = 1
        if converged:
            break
        oldsum = newsum

    return t,r,c,z
