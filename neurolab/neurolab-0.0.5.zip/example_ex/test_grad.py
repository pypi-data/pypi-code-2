# -*- coding: utf-8 -*-
"""
Проверка расчета градиента,
сравнение с библиотекой netff
"""
import numpy as np
import neurolab as nl
import ffnet
from neurolab import trans

conec = ffnet.mlgraph( (1,5, 10, 1) )
net = ffnet.ffnet(conec)

input = [[1.], [2.], [3.], [4.]]
target = [[0.5], [1.0], [1.5], [2.0]]

#input = [[1.0]]
#target = [[1.0]]
net.weights.fill(0.3)
gr1 = net.grad(input, target)
gr1.sort()

net2  = nl.net.newff([[-0.5, 0.5]], [5, 10, 1])
for l in net2.layers:
    l.np['w'].fill(0.3)
    l.np['b'].fill(0.3)
    l.transf = trans.LogSig()

gr2 = nl.train.ff_grad(net2, input, target)

gr3 = []
for l in gr2:
    gr3.extend(l['w'].flatten().tolist())
    gr3.extend(l['b'].tolist())
    
gr2 = np.array(gr3)
gr2.sort()


print gr1 == gr2