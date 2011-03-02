# -*- coding: utf-8 -*-
"""
Некоторые вспомогательные функции

"""
import numpy as np

def minmax(input):
    input = np.asfarray(input)
    assert input.ndim == 2
    min = input.min(axis=0)
    max = input.max(axis=0)
    out = [x for x in zip(min, max)]
    return tuple(out)

def shuffle(*args):
    """Mixing 2 array on axis 1
    
    """
    ind = np.arange(len(args[0]))
    np.random.shuffle(ind)
    
    res = []
    for a in args:
        res.append( np.take(a,ind,0))
    
    return tuple(res)


class Norm:
    def __init__(self, x):
        
        x = np.asfarray(x)
        if(len(x.shape)) == 1:
            ValueError(u'x shape must be like (M, N)')
        min = np.min(x, axis=0)
        dist = np.max(x, axis=0) - min
        
        min.shape = 1, min.size
        dist.shape = 1, dist.size
        
        self.min = min
        self.dist = dist
    
    def __call__(self, x):
        x = np.asfarray(x)
            
        res = (x - self.min) / self.dist
        
        return res
    
    def renorm(self, x):
        x = np.asfarray(x)
        
        res = x * self.dist + self.min
        return res
    

def load(fname):
    from cPickle import load
    
    file = open(fname, 'r')
    net = load(file)
    file.close()
    
    return net
    
def save(net, fname):
    from cPickle import dump
    file = open(fname, 'w')
    dump(net, file)
    file.close()
    
def np_size(net):
    size = 0
    for l in net.layers:
        for prop in l.np.values():
            size += prop.size
    return size

def np_get(net, size):
    result = np.zeros(size)
    start = 0
    for l in net.layers:
        for prop in l.np.values():
            result[start : start+prop.size] = prop.flat[:]
            start += prop.size
    return result

def np_set(net, np_data):
    start = 0
    for l in net.layers:
        for prop in l.np:
            size = l.np[prop].size
            values = np_data[start : start+size]
            values.shape = l.np[prop].shape
            l.np[prop][:] = values
            start += size

#------------------------------------------------------------

def ff_grad_step(net, inp, tar, deriv, grad=None):
    delt = [None] * len(net.layers)
    out = net.step(inp)
    bp = range(len(net.layers) -1, -1, -1)
    if grad is None:
        grad = [{'w': np.zeros(l.np['w'].shape), 
                 'b': np.zeros(l.np['b'].shape)} for l in net.layers]
    for ln in bp:
        layer = net.layers[ln]
        if ln == len(net.layers)-1:
            e = out - tar
            delt[ln] = deriv(e) * layer.transf.deriv(layer.s, out)
        else:
            # For hidden layers
            next = ln + 1
            dS = np.sum(net.layers[next].np['w'] * delt[next], axis=0)
            delt[ln] = dS * layer.transf.deriv(layer.s, layer.out)
            
        delt[ln].shape = delt[ln].size, 1
        grad[ln]['w'] += delt[ln] * layer.inp
        grad[ln]['b'] += delt[ln].reshape(delt[ln].size)
    return grad
    
def ff_grad(net, input, target, deriv):
    grad = [{'w': np.zeros([l.cn,l.ci]), 'b': np.zeros(l.cn)} for l in net.layers]
    for inp, tar in zip(input, target):
        ff_grad_step(net, inp, tar, deriv, grad)
    return grad