#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright INRIA
# Contributors: Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
#
# DANA is a computing framework for the simulation of distributed,
# asynchronous, numerical and adaptive models.
#
# This software is governed by the CeCILL license under French law and abiding
# by the rules of distribution of free software. You can use, modify and/ or
# redistribute the software under the terms of the CeCILL license as circulated
# by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info/index.en.html.
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean that
# it is complicated to manipulate, and that also therefore means that it is
# reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# -----------------------------------------------------------------------------
import Image
from dana import *
from display import *

n = 64
p = 2*n+1
alpha, tau, h = 10.0, 0.1, 0

filename = 'test.png'
image = np.asarray(Image.open(filename).convert('RGB').resize((n,n)))/256.0
image = image.view(dtype=[('r',float), ('g',float), ('b',float)]).squeeze()
image = image[::-1,::]
r, g, b = image['r'], image['g'], image['b']

I = (0.212671*r + 0.715160*g + 0.072169*b)
R,G,B,Y = r - (g+b)/2, g-(r+b)/2, b-(r+g)/2, (r+g)/2-np.abs(r-g)/2-b
for Z in [I,R,G,B,Y]:
    Z[...] = (Z-Z.min())/(Z.max()-Z.min())
    Z += (1-2*rnd.random((n,n)))*.05

focus = Group((n,n), '''dU/dt = alpha*(-V + tau*(L+I)) +h : float
                         V    = np.maximum(U,0)           : float
                         I                                : float
                         L                                : float''')
SparseConnection(I, focus('I'), gaussian((5,5), .5)) # .1*np.ones((1,1)))
SharedConnection(focus('V'), focus('L'),
                 (1.25*gaussian((p,p),0.1) - 0.75*gaussian((p,p),1.0))*(45*45)/(n*n))

V = []
focus.setup()
for i in range(int(3/0.005)):
    focus.evaluate(dt=0.005)
    V.append(focus.V.max())
#run(t=25.0, dt=0.05)

mpl.rcParams['axes.titlesize']      = 'small'
mpl.rcParams['image.cmap']          = 'gray'
mpl.rcParams['image.origin']        = 'upper'
mpl.rcParams['image.interpolation'] = 'nearest'

fig = plt.figure(figsize=(10,10), facecolor='white')
plot(plt.subplot(1,3,1), focus('I'), 'Intensity')
plot(plt.subplot(1,3,2), focus('V'), 'Focus',  cmap= plt.cm.PuOr_r)
plt.subplot(1,3,3),
plt.plot(V)
plt.connect('button_press_event', button_press_event)
plt.show()

