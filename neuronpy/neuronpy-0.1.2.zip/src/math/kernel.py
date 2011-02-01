# -*- coding: utf-8 -*-
"""
Kernel generating functions.

AUTHORS:

- THOMAS MCTAVISH (2010-02-05): initial version

- THOMAS MCTAVISH (2011-01-12): Fixed bug where kernels did not normalize with dt.
"""
# While this software is under the permissive MIT License, 
# (http://www.opensource.org/licenses/mit-license.php)
# We ask that you cite the neuronpy package (or tools used in this package)
# in any publications and contact the author with your referenced publication.
#
# Format:
# McTavish, T.S. NeuronPy library, version 0.1, http://bitbucket.org/tommctavish/neuronpy
#
# Copyright (c) 2010 Thomas S. McTavish
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy

def gauss_1d(sigma=1., dt=1., limit=.01, normalize=True):
    """
    Get a Gaussian distribution that sums to 1 along 1 dimension, 
    quantized by discrete steps.
    """
    tail=[]
    x=0.
    val=1.
    two_times_sigma_squared=2*sigma*sigma
    scale_factor = 1./numpy.sqrt(two_times_sigma_squared*numpy.pi)
    while val > limit:
        val = float(numpy.exp(-(x*x)/two_times_sigma_squared)*scale_factor)
        tail.append(val)
        x+=dt

    k=tail[::-1]   # Make a copy of the reversed tail
    k.extend(tail[1:]) # Reflect
    
    # Normalize
    if normalize:
        k = numpy.divide(k,numpy.sum(k)/dt)
    
    return k
    
def triangle(dt=.1, normalize=True):
    """
    Make a ramp from 0 to 1 back to 0 again by dt.
    """
    k = numpy.arange(dt, 1, dt)
    k = numpy.concatenate((k, numpy.arange(1, 0, -dt)))
    
    # Normalize
    if normalize:
        k = numpy.divide(k,numpy.sum(k)/dt)
    
    return k