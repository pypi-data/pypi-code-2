#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# DANA - Distributed (Asynchronous) Numerical Adaptive computing framework
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
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

