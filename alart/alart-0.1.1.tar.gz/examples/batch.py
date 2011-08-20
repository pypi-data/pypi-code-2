#!/usr/bin/env python
# -*- coding: utf-8 -*-

# alart: a pseudo-random art generator
# Copyright (C) 2010, 2011  Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

## Maintainer: Niels Serup <ns@metanohi.name>
# Output 10 images in a row

from __future__ import with_statement # For Python 2.5
import alart

size = (100, 100)
formats = ('svg', 'png')
gen = alart.Alart(size, formats)

for i in range(10):
    print 'Generating image...',
    data = gen.generate()
    print '\tdone.'
    fname = 'test%d' % i
    print 'Saving to %s.{svg,png}...' % fname,
    with open('%s.svg' % fname, 'w') as f:
        f.write(data['svg'])
    with open('%s.png' % fname, 'wb') as f:
        f.write(data['png'])
    print '\tdone.'
