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
'''
This example shows various connections and how to display them.
'''
from dana import *

n = 5
p = 2*n+1

Z_n   = Group((n, ),'V')
Z_n_1 = Group((n,1),'V')
Z_1_n = Group((1,n),'V')
Z_n_n = Group((n,n),'V')
print Z_n_1
#print Z_1_n
print
print Z_n_n
print

C = DenseConnection(Z_n_n, Z_1_n, np.ones((p,1)))
print C.weights[0].reshape((n,n))
print C.weights[4].reshape((n,n))

C = DenseConnection(Z_n_n, Z_n_1, np.ones((1,p)))
print C.weights[0].reshape((n,n))
print C.weights[4].reshape((n,n))

