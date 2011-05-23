#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 19:13:28 2011

@ author:                  Sat Kumar Tomer 
@ author's webpage:        http://civil.iisc.ernet.in/~satkumar/
@ author's email id:       satkumartomer@gmail.com
@ author's website:        www.ambhas.com

"""
from __future__ import division
from scipy.stats import *
import random as R
from pylab import*
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d

def integrand_debye(t,alpha):
    return t/(alpha*(np.exp(t)-1))

def debye(alpha):
    return quad(integrand_debye, 0, alpha, args=(alpha))[0]

vec_debye = np.vectorize(debye)


def copularnd(family,a,n):
    """
    Input:
        family:   clayton or frank or gumbel
        a:        parameter of copula
        n:        number of random copula to be generated
    Output:
        U and V:  generated copula
        
    Example:
        >>> U,V = copularnd(clayton,2.0,100)
    """
    
    # CLAYTON copula
    if family == 'clayton':
        U = []
        P = []
        for i in range(n):
            U.append(R.random())
            P.append(R.random())
        U = np.array(U)
        P = np.array(P)
        
        if a < 0:
            print 'error: the parameter for clayton copula should be nonnegative'
        
        if a < sys.float_info.epsilon :
            V = P
        else:
            V = U*(P**(-a/(1 + a)) - 1 + U**a)**(-1/a)
    
    # FRANK copula
    elif family == 'frank':
        U = []
        P = []
        for i in range(n):
            U.append(R.random())
            P.append(R.random())
        U = np.array(U)
        P = np.array(P)
        
        if abs(a) > log(sys.float_info.max):
            V = (U < 0) + sign(a)*U
        elif abs(a) > sqrt(sys.float_info.epsilon):
            V = -np.log((np.exp(-a*U)*(1-P)/P + np.exp(-a))/(1 + np.exp(-a*U)*(1-P)/P))/a
        else:
            V = P
    
    # GUMBEL copula
    elif family == 'gumbel':
        if a < 1 :
            print 'error: the parameter for GUMBEL copula should be greater than 1'
        if a < 1 + sys.float_info.epsilon:
            U = []
            V = []
            for i in range(n):
                U.append(R.random())
                V.append(R.random())
            U = np.array(U)
            V = np.array(V)
        else:
            u = []
            p = []
            p1 = []
            p2 = []
            for i in range(n):
                u.append(R.random())
                p.append(R.random())
                p1.append(R.random())
                p2.append(R.random())
            u = np.array(u)
            p = np.array(p)
            p1 = np.array(p1)
            p2 = np.array(p2)
            
            u = (u - 0.5) * pi
            u2 = u + pi/2;
            e = -np.log(p)
            t = cos(u - u2/a)/ e
            gamma = (np.sin(u2/a)/t)**(1/a)*t/np.cos(u)
            s1 = (-np.log(p1))**(1/a)/gamma
            s2 = (-np.log(p2))**(1/a)/gamma
            U = np.array(np.exp(-s1))
            V = np.array(np.exp(-s2))
    else:
        print 'the family of copula not understood'
    
    return U,V

def copulafit(family,x,y):
    """
    Input:
        family:   clayton or frank or gumbel
        x and y:  input vectors of data
    
    Output:
        a:   parameter of copula
    
    Example:
        >>> x = np.random.rand(100)
        >>> y = np.random.randn(100)
        >>> a = copulafit('clayton',x,y)
    """
    tau = kendalltau(x,y)[0]
    if family == 'clayton':
        a = 2*tau/(1 - tau)
    
    elif family == 'frank':
        right = (1-tau)/4.0
        alpha = np.linspace(-100,100000,900)
        left = (vec_debye(alpha)-1)/alpha
        err = left-right
        if err.max()<-1e-3:
            print 'could not find the exact paramter'
            err[err.argmax()] = 0.01
        f = interp1d(err,alpha)
        a = f(0)

    elif family == 'gumbel':
        a = 1/(1-tau)
    else:
       print 'the family of copula not understood'
    return a





