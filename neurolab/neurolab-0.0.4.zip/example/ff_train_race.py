# -*- coding: utf-8 -*-
""" Тестирование градиентных алгоритмов обучения

"""

import neurolab as nl
import numpy as np
import pylab as pl
import time

# Задача аппроксимации функции 1/2 * sin(x)
x = np.linspace(-7, 7, 20)
y = np.sin(x) * 0.5

size = len(x)

input = x.reshape(size, 1)
target = y.reshape(size, 1)

# Create network with 2 layers and rendom initialized
net = nl.net.newff([[-0.5, 0.5]], [5, 1])

trains = [nl.train.TrainGD(), 
          nl.train.TrainGDM(), 
          nl.train.TrainRprop(), 
          nl.train.TrainRpropM(),
          nl.train.TrainCG(),
          nl.train.TrainBFGS(),
          ]

errors, times = [], []
for train in trains:
    net.trainf = train
    cnet = net.copy()
    cnet.train(input, target, epochs=1, show=0, goal=0)
    cnet = net.copy()
    st = time.clock()
    e = cnet.train(input, target, epochs=100, show=0, goal=0)
    times.append(time.clock() - st)
    errors.append(e)
    

lables = [str(s)[16 : str(s).find(' ')] for s in trains]
ind = np.arange(len(errors))
width = 0.8
pl.subplot(211)
pl.bar(ind, [e[-1] for e in errors], width)
pl.ylabel('Result error')
pl.xticks(ind + width/2, lables)

pl.subplot(212)
pl.bar(ind, times, width)
pl.ylabel('Time work')

pl.xticks(ind + width/2, lables)

pl.show()