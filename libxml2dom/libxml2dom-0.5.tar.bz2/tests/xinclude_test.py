#!/usr/bin/env python

import libxml2dom

s = """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:xi="http://www.w3.org/2001/XInclude">
<body>
  <p>
    <xi:include href="tests/test_xinclude.xhtml"
      xpointer="xmlns(html=http://www.w3.org/1999/xhtml)xpointer(/html:html/html:body/html:p/node())"/>
  </p>
</body>
</html>
"""

d = libxml2dom.parseString(s)
print "Result of XInclude processing:", d.xinclude()
print
print d.toString()

# vim: tabstop=4 expandtab shiftwidth=4
