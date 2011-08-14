#!/usr/bin/env python3

# testVectors32.py - test unit to verify the sanity of vectors32
#                    module.

# Copyright (C) 2011 Algis Kabaila 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later 
# version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free 
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301  USA
# You can contact the author by email algis.kabaila@gmail.com or
# paper mail PO Box 279 Jamison Centre ACT 2614 Australia.

'''
>>> v1 = Vector(2.0, 3.0, 4.0)
>>> v2 = Vector(6.6, 5.5, 4.5)
>>> print(v1)
Vector(2.0, 3.0, 4.0)
>>> print(v2)
Vector(6.6, 5.5, 4.5)
>>>
# Properties
# ---------
>>> v3 = Vector(5.0, 6.0 ,7.0)
>>> print(v3)
Vector(5.0, 6.0, 7.0)
>>> v3.size
10.488088481701515
>>> v4 = v3.normalize
>>> print(v3)
Vector(5.0, 6.0, 7.0)
>>> print(v4)
Vector(0.4767312946227962, 0.5720775535473553, 0.6674238124719146)
>>>
# Vector addition and subtraction
# -------------------------------
>>> w1 = v1 + v2
>>> w2 = w1 - v2
>>> print(w1)
Vector(8.6, 8.5, 8.5)
>>> print(w2)
Vector(2.0, 3.0, 4.0)
>>>
# Multiplication, all forms.
#--------------------------
# Scaling (multiply by a scalar)M.
>>> w1 = 2 * v1
>>> print(v1)
Vector(2.0, 3.0, 4.0)
>>> w2 = v2 * 2
>>> print(w2)
Vector(13.2, 11.0, 9.0)
>>> w1 = v1 * 1.5
>>> print(w1)
Vector(3.0, 4.5, 6.0)
>>> 
# Scalar (dot) product.
# The result is scalar.
>>> s = v1 * v2
>>> print(s)
47.7
>>> s = v2 * v1
>>> print(s)
47.7
>>>
# Vector (cross) product.
>>> v1 = Vector(1, 2, 3.0)
>>> v2 = Vector(7., 6, 5)
>>> w1 = v1 ** v2
>>> print(w1)
Vector(-8.0, 16.0, -8.0)
>>> w2 = v2 ** v1
>>> print(w2)
Vector(8.0, -16.0, 8.0)
>>> 
'''
from vectors32 import vectors32
Vector = vectors32.Vector

import doctest
doctest.testmod()

print('vectors32 module verification:')
print('If no errors reported, all is well.')
