#!/usr/bin/env python
import hide as H
from bitstring import BitArray
c = H.Concealer()
src = BitArray(bytes=open('rofl', 'rb').read())
print 'src: %s' % src
x = c.conceal(src)
print 'ciphertext: %s' % x
y = c.reveal(x)
print 'cleartext: %s' % y
