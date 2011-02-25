# -*- coding: utf-8 -*-
"""
The module contains the basic layers architectures

"""
from core import Layer
import init
import trans

import numpy as np


class Perceptron(Layer):
    """
    Perceptron Layer class
    :Example:
        >>> # create layer with 2 inputs and 4 outputs(neurons)
        >>> l = layer.Perceptron(2, 4, trans.PureLin())
    """
    def __init__(self, ci, cn, transf):
        """
        :Parameters:
            ci: int
                Number of input
            cn: int
                Number of neurons
            transf: callable
                transfer function

        """
        Layer.__init__(self, ci, cn, cn, ['w','b'])
        
        self.transf = transf
        if not hasattr(transf, 'out_minmax'):
            Inf = 1e100
            self.out_minmax = np.array([(self.transf(-Inf), self.transf(Inf))] * self.co)
        else:
            self.out_minmax = np.array([np.asfarray(transf.out_minmax)] * self.co)

        # init propertys default zero:
        self.np['w'] = np.zeros([self.cn, self.ci])
        self.np['b'] = np.zeros(self.cn)
        
        self.initf = init.initwb_reg
        # 
        self.s = np.zeros(self.cn)

    def _step(self, inp):
        
        self.s = np.sum(self.np['w'] * inp, axis=1)
        self.s += self.np['b']
        return self.transf(self.s)
     

class Competitive(Layer):
    """ 
    Competitive Layer class
    
    """
    def __init__(self, ci, cn, distf=None):
        """
        :Parameters:
            ci: int
                Number of input
            cn: int
                Number of neurons
            distf: callable default(euclidean)
                
        """
        Layer.__init__(self, ci, cn, cn, ['w','conscience'])
        self.transf = trans.Competitive()
        self.out_minmax = np.array([self.transf.out_minmax])
        
        self.np['w'] = np.zeros([self.cn, self.ci])
        self.np['conscience'] = np.ones(self.cn)
        
        # default distance function
        # see scipi.spatial.distance.cdist()
        def euclidean(A, B):
            dist = np.sum(np.square(A-B) ,axis=1)
            return dist
        
        self.distf = euclidean
    
    def _step(self, inp):

        d = self.distf(self.np['w'], inp.reshape([1,len(inp)]))
        self.last_dist = d
        out = self.transf(self.np['conscience'] * d)
        return out