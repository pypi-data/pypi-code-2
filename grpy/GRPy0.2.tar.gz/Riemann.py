#!/usr/bin/env python
################################################################################
# File: Riemann.py
# Author: Sergei Ossokine
# This contains the implementation of the following GR-related quantities:
# Riemann cruvature tensor, Ricci tensor, Ricci scalar, Einstein tensor
# Last Modified: Auhust 28th, 2009
# This file is part of GRPy, a small GR-oriented package based on sympy.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see:
# http://www.gnu.org/licenses/gpl.html.
################################################################################

from Tensor import Tensor,Metric

from sympy import diff,trim,together,ratsimp,simplify
from numpy import arange,pi


class Riemann(Tensor):
    '''This is a class to represent the completely covariant 
    Riemann curvature tensor in a basis. We first compute the tensor
    with the last indexed raised, then we lower it'''
    def __init__(self,Chris):
    	
    	super(Riemann,self).__init__('R_{abcd}',(0,4),(-1,-1,-1,-1),\
    		coords=Chris.g_down.coords)
    	
    	R_temp = Tensor('R_{abc}^{d}',(1,3),(-1,-1,-1,1),\
    		coords=Chris.g_down.coords)
    	self.g_down = Chris.g_down
	self.g_up = Chris.g_up
    	for a in arange(self.dim):
	    for b in arange(self.dim):
		for c in arange(self.dim):
		    for d in arange(self.dim):
			sum = 0.0
    			for al in range(self.dim):
			    term = Chris[al,-a,-c]*Chris[d,-al,-b] \
				 - Chris[al,-b,-c]*Chris[d,-al,-a]
			    sum += term
    			t1 = diff(Chris[d,-a,-c],self.coords[b])
    			t2 = diff(Chris[d,-b,-c],self.coords[a])
    			res = t1 - t2 + sum
                        
			R_temp.components[-a,-b,-c,d] = res
        
	for a in arange(self.dim):
            for b in arange(self.dim):
                for c in arange(self.dim):
                	for d in range(self.dim):
                		sum = 0.0
                		for f in arange(self.dim):
                    	
				    sum +=self.g_down[-d,-f]*R_temp[-a,-b,-c,f]
				
				
                                self.components[-a,-b,-c,-d] = sum
                    	
                   	
	self.getNonZero()

class Ricci(Tensor):
    ''' This class represents the Ricci curvature tensor'''
    
    def __init__(self,Riem):
        super(Ricci,self).__init__('R_{ab}',(0,2),(-1,-1),coords =Riem.coords)
        
	self.g_up = Riem.g_up
        for a in arange(self.dim):
            for b in arange(self.dim):
                sum = 0.0
                
                for l in range(self.dim):
                    for k in range(self.dim):
			sum += self.g_up[l,k]*Riem[-a,-l,-b,-k]
                    
                
                
                self.components[-a,-b] = sum
       
        self.getNonZero()

class RicciScalar(object):
    
	def __init__(self,metric,Ricci):
		g_up = metric.inverse
		sum = 0.0
		for i in arange(metric.dim):
			for j in arange(metric.dim):
				sum += g_up[i,j]*Ricci[-i,-j]
		self.R = sum
    
	def __str__(self):
		return str(self.R)
        def __repr__(self):
            return self

class EnMt(Tensor):
    '''Computes the energy-momnetum tensor from Einstein field equations
        Note that the factor of 1/(8*pi) was dropped for convenience'''
    def __init__(self,metric,Ric,RS):
        super(EnMt,self).__init__('T_{ab}',(0,2),(-1,-1),coords =Ric.coords)
        g_down = metric
        for a in arange(self.dim):
            for b in arange(self.dim):
                self.components[-a,-b] = Ric[-a,-b] - 0.5*RS.R*g_down[-a,-b]
                
class Kretschmann(object):
    def __init__(self):
        print "Not yet implemented!"
