#!/usr/bin/env python

import libxml2dom.xmlrpc

m1 = libxml2dom.xmlrpc.createMethodCall("hello")
m1.parameterValues = ["1", [1.0, (2, "3")], 1, {4: 5, "a": "b"}]
print m1.parameterValues

m2 = libxml2dom.xmlrpc.createMethodCall("hello")
m2.parameterValues = [[1.0, (2, "3")], [2, "3"]]
print m2.parameterValues

print m2.parameterValues[0], m2.parameterValues[1]
assert m2.parameterValues[0] != m2.parameterValues[1]

print m2.parameters[0], m2.parameters[1]
assert m2.parameters[0] != m2.parameters[1]

print m2.parameterValues[0][1], m2.parameterValues[1]
assert m2.parameterValues[0][1] == m2.parameterValues[1]

print m2.parameters[0][1], m2.parameters[1]
assert m2.parameters[0][1] == m2.parameters[1]

# vim: tabstop=4 expandtab shiftwidth=4
