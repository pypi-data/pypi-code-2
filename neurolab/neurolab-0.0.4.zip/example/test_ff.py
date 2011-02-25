# -*- coding: utf-8 -*-
""" Пример использования сети полученной newff

"""

import neurolab as nl
import numpy as np
import neurolab.trans as trans

net = nl.net.newff([[0.0, 1.0], [0.0, 1.0]],[3, 1])

net.layers[0].np['w'].fill(1.0)
net.layers[0].np['b'].fill(0.0)
net.layers[0].transf = trans.PureLin()

net.layers[1].np['w'] = np.array([[10, 20, 30]])
net.layers[1].np['b'] = np.array([15])
net.layers[1].transf = trans.PureLin()
# res = 2*10 + 2*20 +2*30 +15
res = net.step(np.ones(2))[0]

assert res == 2*10 + 2*20 +2*30 +15



