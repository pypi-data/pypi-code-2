#!/usr/bin/python
"""
Implements the Latin Hypercube Sampling technique as described by Iman and Conover, 1982, including correlation control
both for no correlation or for a specified correlation matrix for the sampled parameters
"""
import random
import scipy.stats
import numpy
from numpy.linalg import * 
from pylab import *
#import psyco
#psyco.full()

def rank_restr(nparms=4, Iter=100, noCorrRestr=True, matCorr=None):
    """
    please Add docstring
    """
    x=[]
    if noCorrRestr:
        for i in xrange(nparms):
            x.append(numpy.array(random.sample(xrange(1,Iter+1), Iter)))
        return x
    else:
        if matCorr==None:
            C=numpy.core.numeric.identity(nparms)
        else:
            C=numpy.matrix(matCorr)
        s0=numpy.arange(1.,Iter+1)/((Iter*1.)+1)
        s=scipy.stats.norm().ppf(s0)
        s1=[]
        for i in xrange(nparms):
            random.shuffle(s)
            s1.append(s.copy())
        S=numpy.matrix(s1).transpose()
        
        E=corrcoef(S.transpose())
        P=cholesky(C)
        Q=cholesky(E)
        Final=S*inv(Q).transpose()*P.transpose()
        for i in xrange(nparms):
            x.append(scipy.stats.stats.rankdata(Final.transpose()[i,]))
        return x

def sample_cum(Iter=100):
    """
    """
    segmentSize = float(1./Iter)
    samples=[]
    points = scipy.stats.uniform.rvs(size=Iter)*segmentSize+arange(Iter)*segmentSize
    return list(points)


def sample_dist(cum, dist='Normal', parms=[0,1]):
    """
    """
    if dist == 'Normal':
        if len(parms) == 2:
            n = scipy.stats.norm(parms[0],parms[1])
            d = n.ppf(cum)
    elif dist=='Triangular':
        if len(parms) ==3 and parms[0]<=parms[1]<=parms[2]:
            loc=parms[0]
            scale=parms[2]-parms[0]
            t = scipy.stats.triang((float(parms[1])-loc)/scale,loc=loc,scale=scale)
            d = t.ppf(cum)
    elif dist == 'Uniform':
        loc = parms[0]
        scale = parms[1]-parms[0]
        d = scipy.stats.uniform(loc,scale).ppf(cum)
    else:
        print '%s is and unsupported distribution!'%dist
    return d



def lhs(Pars, dists, parms, Iter=100, noCorrRestr=True, matCorr=None):
    """
    Adicionar docstring
    """
    ParsList=[]
    if len(Pars)==len(dists):
        indexes=rank_restr(nparms=len(dists), Iter=Iter, noCorrRestr=noCorrRestr, matCorr=matCorr)
        for i in xrange(len(Pars)):
            v=sample_dist(sample_cum(Iter), dist=dists[i], parms=parms[i])
            index=map(int,indexes[i]-1)
            ParsList.append(v[index])
    return ParsList
            
    

if __name__=='__main__':
    #c=lhs(['Par1', 'Par2', 'Par3'],['Normal','Triangular','Uniform'], [[0,1], [1,5,8], [1,2]],100000)
    c=lhs(['Par1', 'Par2', 'Par3'],['Normal','Triangular','Uniform'], [[0,1], [1,5,8], [1,2]],100000, noCorrRestr=False)
  #  m=[[1,.3595,-.2822],[.3595,1,-.1024],[-.2822,-.1024,1]]
  #  c=lhs(['Par1', 'Par2', 'Par3'],['Normal','Triangular','Uniform'], [[0,1], [1,5,8], [1,2]],100000, noCorrRestr=False, matCorr=m)
    print scipy.stats.stats.spearmanr(c[0],c[1])
    print scipy.stats.stats.spearmanr(c[0],c[2])
    print scipy.stats.stats.spearmanr(c[1],c[2])
    
    
    
    #a=sample_cum(10000)
    #b=sample_dist(a, dist='Triangular', parms=[1,5,8])
    
    #plot(b,a, 'bo')
    """
    hist(c['Par1'], bins=30)
    figure()
    hist(c['Par2'], bins=30)
    figure()
    hist(c['Par3'], bins=30)
    show()
    
    
    """
