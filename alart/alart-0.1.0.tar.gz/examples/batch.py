#!/usr/bin/env python
#~Public domain
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
