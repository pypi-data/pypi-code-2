# -*- coding: utf-8 -*-
""" Пример использования сети полученной newff

"""

import neurolab as nl
import numpy as np




# Задача аппроксимации функции 1/2 * sin(x)
x = np.linspace(-7, 7, 20)
y = np.sin(x) * 0.5

size = len(x)

inp = x.reshape(size,1)
tar = y.reshape(size,1)

# Create network with 2 layers and rendom initialized
net = nl.net.newff([[-0.5, 0.5]],[5, 1])
net.trainf = nl.train.TrainRprop()
error = net.train(inp, tar, epochs=500, show=100, goal=0.02)

out = net.sim(inp)

pl.subplot(211)
pl.plot(error)
pl.xlabel('Epoch number')
pl.ylabel('error (default SSE)')

x2 = np.linspace(-6.0,6.0,150)
y2 = net.sim(x2.reshape(x2.size,1)).reshape(x2.size)

y3 = out.reshape(size)

pl.subplot(212)
pl.plot(x2, y2, '-',x , y, '.', x, y3, 'p')
pl.legend(['train target', 'train result'])
pl.show()


