#!/usr/bin/env python

import libxml2dom
import sys

d = libxml2dom.parse(sys.argv[1])

print "Prettyprint using libxml2dom..."
print

d.toStream(sys.stdout, prettyprint=1)

try:
    from xml.dom.ext import PrettyPrint

    print "Prettyprint using xml.dom..."
    print

    PrettyPrint(d)

except ImportError:
    print "xml.dom not tested."

# vim: tabstop=4 expandtab shiftwidth=4
