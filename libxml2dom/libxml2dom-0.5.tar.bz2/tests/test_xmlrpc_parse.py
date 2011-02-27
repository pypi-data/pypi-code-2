#!/usr/bin/env python

import libxml2dom.xmlrpc

# Some examples from the specification.

request = """<?xml version="1.0"?>
<methodCall>
   <methodName>examples.getStateName</methodName>
   <params>
      <param>
         <value><i4>41</i4></value>
      </param>
   </params>
</methodCall>"""

req = libxml2dom.xmlrpc.parseString(request)
print "Method name:", req.method.methodName
print "Parameter values:", req.method.parameterValues
print "Fault:", req.fault
assert req.method.methodName == "examples.getStateName"
assert req.method.parameterValues == [41]
assert req.method.parameters[0].valueElement.container == 41
assert req.method.params.values()[0] == 41
assert req.fault is None

response = """<?xml version="1.0"?>
<methodResponse>
   <params>
      <param>
         <value><string>South Dakota</string></value>
      </param>
   </params>
</methodResponse>"""

resp = libxml2dom.xmlrpc.parseString(response)
print "Method name:", resp.method.methodName
print "Parameter values:", resp.method.parameterValues
print "Fault:", resp.fault
assert resp.method.methodName is None
assert resp.method.parameterValues == ["South Dakota"]
assert resp.fault is None

failed = """<?xml version="1.0"?>
<methodResponse>
   <fault>
      <value>
         <struct>
            <member>
               <name>faultCode</name>
               <value><int>4</int></value>
               </member>
            <member>
               <name>faultString</name>
               <value><string>Too many parameters.</string></value>
            </member>
         </struct>
      </value>
   </fault>
</methodResponse>"""

f = libxml2dom.xmlrpc.parseString(failed)
print "Method name:", f.method.methodName
print "Parameter values:", f.method.parameterValues
print "Fault code:", f.fault.code
assert f.method.methodName is None
assert f.method.parameterValues is None
assert f.fault.code == "4"
assert f.fault.reason == "Too many parameters."

# Python Package Index examples.

search = """<?xml version="1.0"?>
<methodCall>
  <methodName>search</methodName>
  <params>
    <param>
      <value>
        <struct>
          <member>
            <name>name</name>
            <value><string>libxml2dom</string></value>
          </member>
          <member>
            <name>description</name>
            <value>XML</value>
          </member>
        </struct>
      </value>
    </param>
    <param>
      <value>
        <string>and</string>
      </value>
    </param>
  </params>
</methodCall>"""

s = libxml2dom.xmlrpc.parseString(search)
print "Method name:", s.method.methodName
print "Parameter values:", s.method.parameterValues
print "Fault:", s.fault
assert s.method.methodName == "search"
assert s.method.parameterValues == [
    [
        ("name", "libxml2dom"),
        ("description", "XML")
        ],
    "and"
    ]
assert s.fault is None

# Nested structure examples.

search2 = """<?xml version="1.0"?>
<methodCall>
  <methodName>search</methodName>
  <params>
    <param>
      <value>
        <struct>
          <member>
            <name>names</name>
            <value>
              <struct>
                <member>
                  <name>name</name>
                  <value><string>libxml2dom</string></value>
                </member>
                <member>
                  <name>description</name>
                  <value>XML</value>
                </member>
              </struct>
            </value>
          </member>
        </struct>
      </value>
    </param>
    <param>
      <value>
        <string>and</string>
      </value>
    </param>
  </params>
</methodCall>"""

s2 = libxml2dom.xmlrpc.parseString(search2)
print "Method name:", s2.method.methodName
print "Parameter values:", s2.method.parameterValues
print "Fault:", s2.fault
assert s2.method.methodName == "search"
assert s2.method.parameterValues == [
    [
        ("names", [
            ("name", "libxml2dom"),
            ("description", "XML")
            ])
        ],
    "and"
    ]
assert s2.fault is None

arrays = """<?xml version="1.0"?>
<methodResponse>
  <params>
    <param>
      <value>
        <array>
          <data>
            <value>
              <string>libxml2dom</string>
            </value>
            <value>
              <string>XSLTools</string>
            </value>
          </data>
        </array>
      </value>
    </param>
  </params>
</methodResponse>"""

a = libxml2dom.xmlrpc.parseString(arrays)
print "Method name:", a.method.methodName
print "Parameter values:", a.method.parameterValues
print "Fault:", a.fault
assert a.method.methodName is None
assert a.method.parameterValues == [["libxml2dom", "XSLTools"]]
assert a.fault is None

# vim: tabstop=4 expandtab shiftwidth=4
