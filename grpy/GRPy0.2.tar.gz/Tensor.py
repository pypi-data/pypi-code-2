#!/usr/bin/env python
################################################################################
# File: Tensor.py
# Author: Sergei Ossokine
# This contains the basic definition fo the Tensor class which can be used to
# store arbitrary-dimensional and arbitrary-rank tensors. It also defines a
# Metric class to represent the rank(0,2) non-degenerate symmetric tensor.
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

# TODO: Either expand or phase out the formalTensor class. Implement the sym
# attribute

# The required imports
import sympy
import numpy as np
import itertools
from copy import deepcopy

class formalTensor(object):
  def __init__(self,rank,symbol):
    self.symbol = sympy.Symbol(symbol)
    self.rank = rank
   
    
class Tensor(object):
  '''A class to represent a tensor in a particular basis'''
  def __init__(self,symbol,rank,shape,sym=None,coords=None,**args):
    self.symbol = sympy.Symbol(symbol) # The symbol to represent this Tensor
    self.coords = coords # The coordinate system we are using for the representation
    self.shape = shape # The shape of the tensor, for example (-1,1) for k_{a}^{b
    self.rank = rank # Rank
    self.contr = rank[0]
    self.cov = rank[1]

    # We need to know the dimensionality of our spacetime. For the moment
    # we will deduce it from the coordinates provide, or if none are given, then
    # the assumption will be made that it's stored in the optional arguments
    if coords is not None:
        self.dim = len(self.coords)
    else:
        self.dim = args['dim']

    if coords is not None:
      self.allocate(rank)
      self.rep = True
    self.symbolic = formalTensor(rank,symbol)

  def __setitem__(self,idx,val):
    self.components[idx]=val

  def __getitem__(self,idx):
    return self.components[idx]


  def allocate(self,rank):
    '''Allocate the dictionary(hash table) necessary to store the components
      Note that covariant indices are negative! (except for 0 of course)'''
    n = rank[0] + rank[1]
    indc = list(itertools.product(range(4),repeat=n))
    mastr=[]
    for i in range(len(indc)):
        temp=[]
        for k in range(len(indc[i])):
            
            if self.shape[k] == -1:
                
                temp.append(-indc[i][k])
            else:
                temp.append(indc[i][k])
        mastr.append(tuple(temp))
    self.components = dict(zip(mastr,[0 for i in range(len(indc))]))

  def _dictkeycopy(self, hay):
    keys = hay.keys()
    return dict(zip(keys,[0]*len(keys)))
                
  def getNonZero(self):
    '''Returns only non-zero components of the tensor, if the coordinate
    system is provided'''
    if self.rep:
      nonzerok =[]
      nonzerov = []
      for key in self.components.keys():
        if self.components[key] !=0:
          nonzerok.append(key)
          nonzerov.append(self.components[key])
      d = dict(zip(nonzerok,nonzerov))
      keys = d.keys()
      keys.sort()
      self.nonzero = [(key,d[key]) for key in keys]
      return self.nonzero
    else:
      print "Attempted to get components that have not been initialized!"

  def __str__(self):
    '''Print a "nice" human - readable representation of the tensor'''
    self.getNonZero()
   
    # We will print only non-zero components unless all the components are zero
    ttl=""
    if self.nonzero:
        
      for i in range(len(self.nonzero)):
          ttl += str(self.nonzero[i][0]) + " "+str(self.nonzero[i][1])+"\n"
    else:
      ttl ="All the components of the tensor are 0!"
    return ttl  
  
 

    
class Metric(Tensor):
  '''Represents a metric. Note that coordinates now MUST be provided'''
  
  def __init__(self,coord,rank=(0,2),sh=(-1,-1),symbol='g'):
      self.coord=coord
      super(Metric,self).__init__(symbol,rank,sh,coords=coord)
      
  def invert(self):
      '''Find the inverse of the metric and store the result in a
      Metric object self.inverse'''

      # Store the data in a matrix, invert it using sympy than switch back
      
      temp = sympy.eye(4)
  
      for key in self.components.keys():
          id = tuple(np.abs(key))
          
          temp[id] = self.components[key]
          
      inv = temp.inv()
      inverse = self._dictkeycopy(self.components)
      for i in range(self.dim):
          for j in range(self.dim):
              inverse[i,j] = inv[i,j]
      self.inverse = Metric(self.coord,rank=(2,0),sh=(1,1),symbol='g_inv')
      self.inverse.components = inverse
   




