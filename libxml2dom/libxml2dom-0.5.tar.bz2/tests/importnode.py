#!/usr/bin/env python

import libxml2dom
import sys

test = """<?xml version="1.0"?>
<test>
  <element attr="value">text</element>
</test>
"""

d = libxml2dom.parseString(test)
root = d.documentElement
d2 = libxml2dom.createDocument(None, "new", None)
root2 = d2.documentElement
for i in range(0, 10):
    imported = d2.importNode(root, 1)
    root2.appendChild(imported)
d2.toStream(sys.stdout, prettyprint=1)

# vim: tabstop=4 expandtab shiftwidth=4
