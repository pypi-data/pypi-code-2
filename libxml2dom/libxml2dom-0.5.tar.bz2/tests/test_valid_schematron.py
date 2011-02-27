#!/usr/bin/env python

import libxml2dom

schema = libxml2dom.parse("tests/test_valid_schematron.xml")
d = libxml2dom.parse("tests/test_valid.xml")
print "Test of valid document..."
print d.validate(schema)
print d.validateDocument(schema)
print d.getParameter("error-handler")
print

schema = libxml2dom.parse("tests/test_invalid_schematron.xml")
d = libxml2dom.parse("tests/test_invalid.xml")
print "Test of invalid document..."
print d.validate(schema)
print d.validateDocument(schema)
print d.getParameter("error-handler")
print

# vim: tabstop=4 expandtab shiftwidth=4
