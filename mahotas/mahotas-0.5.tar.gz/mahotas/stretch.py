# -*- coding: utf-8 -*-
# Copyright (C) 2009-2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

from __future__ import division
import numpy as np

__all__ = ['stretch']

def stretch(img, arg0, arg1=None, dtype=np.uint8):
    '''
    img' = stretch(img, max, [dtype=np.uint8])
    img' = stretch(img, min, max, [dtype=np.uint8])

    Contrast stretch the image to the range [0, max] (first form) or
        [min, max] (second form).

    Parameters
    ----------
      img : an np.ndarray. It is *not modified* by this function
      min : minimum value for output [default: 0]
      max : maximum value for output
      dtype : dtype of output [default: np.uint8]
    Returns
    -------
      img': resulting image. ndarray of same shape as img and type dtype.

    Bugs
    ----
        If max > 255, then it truncates the values if dtype is not specified.
    '''
    if arg1 is None:
        min = 0
        max = arg0
    else:
        min = arg0
        max = arg1
    img = img.astype(np.double)
    img -= img.min()
    ptp = img.ptp()
    if not ptp:
        img = np.zeros(img.shape, dtype)
        if min:
            img += min
        return img
    img *= float(max - min)/ptp
    if min: img += min
    return img.astype(dtype)

