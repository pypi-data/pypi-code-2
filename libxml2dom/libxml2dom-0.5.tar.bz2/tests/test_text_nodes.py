#!/usr/bin/env python

"Test text node insertion."

import libxml2dom

d = libxml2dom.createDocument(None, "test", None)

t1 = d.createTextNode("Hello ")
t2 = d.createTextNode("world")
t3 = d.createTextNode("!")

t1x = d.documentElement.appendChild(t1)
t3x = d.documentElement.appendChild(t3)

print d.toString()
assert t2.parentNode is None
assert t1.parentNode is not None
assert t3.parentNode is not None

t2x = d.documentElement.insertBefore(t2, t3)

print d.toString()

l = [n.data for n in t1.parentNode.childNodes]

print l
assert len(l) == 3

# vim: tabstop=4 expandtab shiftwidth=4
