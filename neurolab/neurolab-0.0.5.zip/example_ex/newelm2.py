# -*- coding: utf-8 -*-
""" Пример использования сети полученной newelm

"""

import neurolab as nl
import numpy as np
import pylab as pl

# Идентификация двух единиц

p = np.array([1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1])
t = np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0])
p.shape = len(p), 1
t.shape = len(t), 1

net = nl.net.newelm([[0, 1]], [10, 1])
net.layers[1].initf = nl.init.InitRand([-0.01, 0.01], 'wb')
net.layers[0].initf = nl.init.InitRand([-0.01, 0.01], 'wb')
net.init()
net.layers[1].transf = nl.trans.LogSig()


e = net.train(p, t, epochs=1000, show=100, goal=0.01, lr=0.01, adapt=True)

o = net.sim(p)

pl.plot(t.reshape(t.size))
pl.plot(o.reshape(t.size))

pl.show()