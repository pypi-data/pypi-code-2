# -*- coding: utf-8 -*-
"""
The module contains the basic network architectures

+-------------------------+-------------------+---------+---------------------+-------------------+
|      Network Type       |  Function         |Count of |   Support train     |  Default error    |
|                         |                   | layers  |     functions       |     function      |
+=========================+===================+=========+=====================+===================+
| Single-layer perceptron |    newp           |    1    |     TrainDelta      |        SSE        |
+-------------------------+-------------------+---------+---------------------+-------------------+
| Multi-layer perceptron  |    newff          |  more 1 |     TrainGD,        |        SSE        |
|                         |                   |         |     TrainGDM*,      |                   |
|                         |                   |         |     TrainRprop,     |                   |
|                         |                   |         |     TrainRpropM,    |                   |
|                         |                   |         |     TrainBFGS,      |                   |
|                         |                   |         |     TrainCG         |                   |
+-------------------------+-------------------+---------+---------------------+-------------------+
| Competitive layer       |    newc           |    1    |     TrainWTA,       |        SAE        |
|                         |                   |         |     TrainCWTA*      |                   |
+-------------------------+-------------------+---------+---------------------+-------------------+

.. note:: \* - defaulf function

"""

from core import Net
import trans
import layer
import train
import error

class NetFF(Net):
    
    def __init__(self, inp_minmax, co, layers, trainf):
        connect = [[i-1] for i in range(len(layers) + 1)]
        super(NetFF, self).__init__(inp_minmax, co, layers, connect, trainf)
    


def newff(minmax,size,transf=None):
    """
    Create multilayer perceptron
    
    :Parameters:
        minmax: list ci x 2 
            Range of input value
        size: list of length equal to the number of layers
            Contains the number of neurons for each layer
        transf: list (default TanSig)
            List of activation function for each layer
    :Returns:
        net: Net
    :Example:
        >>> # create neural net with 2 inputs, 1 output and 2 layers
        >>> net = newff([[-0.5, 0.5], [-0.5, 0.5]], [3, 1])
        >>> net.ci
        2
        >>> net.co
        1
        >>> len(net.layers)
        2
        
    """
    
    net_ci = len(minmax);
    net_co = size[-1];
        
    if transf is None:
        transf = [trans.TanSig()]*len(size)
    assert len(transf) == len(size)
    
    layers = []
    for i,nn in enumerate(size):
       layer_ci = size[i-1] if i>0 else net_ci
       l = layer.Perceptron(layer_ci, nn, transf[i])
       layers.append(l)
    net = NetFF(minmax, net_co, layers, train.TrainGD())
    
    return net

def newp(minmax, cn, transf=trans.HardLim()):
    """
    Create one layer perceptron 
        
    :Parameters:
        minmax: list ci x 2
            Range of input value
        cn: int
            Number of neurons
        transf: func (default HardLim)
            Activation function
    :Returns:
        net: Net
    :Example:
        >>> # create nrtwork with 2 inputs and 10 neurons
        >>> net = newp([[-1, 1], [-1, 1]], 10)

    """
        
    ci = len(minmax)
    l = layer.Perceptron(ci, cn, transf)
    net = Net(minmax, cn, [l],  [[-1],[0]], train.TrainDelta())
    return net

def newc(minmax, cn):
    """
    Create competitive layer (Kohonen layer)
    
    :Parameters:
        minmax: list ci x 2
            Range of input value
        cn: int
            Number of neurons
    :Returns:
        net: Net
    :Example:
        >>> # create nrtwork with 2 inputs and 10 neurons
        >>> net = newc([[-1, 1], [-1, 1]], 10)
    
    """
    ci = len(minmax)
    l= layer.Competitive(ci,cn)
    net = Net(minmax, cn, [l], [[-1],[0]], train.TrainCWTA(errorf=error.SAE()))
    
    return net