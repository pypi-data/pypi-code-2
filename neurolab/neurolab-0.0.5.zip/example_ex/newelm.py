# -*- coding: utf-8 -*-
""" Пример использования сети полученной newelm

"""

import neurolab as nl
import numpy as np
import pylab as pl

#TODO: clear_signals()

# определение амплитуд

p1 = np.sin(np.arange(0,20))
p2 = np.sin(np.arange(0,20))

t1 = np.ones([1, 20]) *-0.5
t2 = np.ones([1, 20]) * 0.5

p = np.array([p1, p2, p1, p2])
t = np.array([t1, t2, t1, t2])

p.shape = 20*4, 1
t.shape = 20*4, 1

#net = nl.load('elmtest.net')
net = nl.net.newelm([[-2, 2]], [10, 1])
net.layers[1].initf = nl.init.InitRand([-0.01, 0.01], 'wb')
net.layers[0].initf = nl.init.InitRand([-0.01, 0.01], 'wb')

e = net.train(p, t, epochs=1000, show=100, goal=0.25, adapt=True)
"""
o = net.sim(p)

pl.plot(t.reshape(80))
pl.plot(o.reshape(80))
"""
pl.plot(e)
pl.show()