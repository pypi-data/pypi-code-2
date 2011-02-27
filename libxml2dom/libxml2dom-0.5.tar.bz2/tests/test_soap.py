#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import libxml2dom.soap

request = """<?xml version='1.0' encoding='iso-8859-1'?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope" >
 <env:Header>
   <t:transaction
           xmlns:t="http://thirdparty.example.org/transaction"
           env:encodingStyle="http://example.com/encoding"
           env:mustUnderstand="true" >5</t:transaction>
 </env:Header>  
 <env:Body>
  <m:chargeReservation
      env:encodingStyle="http://www.w3.org/2003/05/soap-encoding"
         xmlns:m="http://travelcompany.example.org/">
   <m:reservation xmlns:m="http://travelcompany.example.org/reservation">
    <m:code>FT35ZBQ</m:code>
   </m:reservation>
   <o:creditCard xmlns:o="http://mycompany.example.com/financial">
    <n:name xmlns:n="http://mycompany.example.com/employees">
           Åke Jógvan Øyvind
    </n:name>
    <o:number>123456789099999</o:number>
    <o:expiration>2005-02</o:expiration>
   </o:creditCard>
  </m:chargeReservation>
 </env:Body>
</env:Envelope>"""

req = libxml2dom.soap.parseString(request)
print "Method name:", req.method.methodName
print "Parameter values:", req.method.parameterValues
print "Fault:", req.fault
print
assert req.method.methodName == "chargeReservation"
assert req.method.parameterValues == [
    ("reservation", [("code", "FT35ZBQ")]),
    ("creditCard", [("name", u"Åke Jógvan Øyvind"),
        ("number", "123456789099999"),
        ("expiration", "2005-02")
        ])
    ]
assert req.fault is None

response = """<?xml version='1.0' encoding='iso-8859-1'?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope" >
 <env:Header>
     <t:transaction
        xmlns:t="http://thirdparty.example.org/transaction"
          env:encodingStyle="http://example.com/encoding"
           env:mustUnderstand="true">5</t:transaction>
 </env:Header>  
 <env:Body>
     <m:chargeReservationResponse 
         env:encodingStyle="http://www.w3.org/2003/05/soap-encoding"
             xmlns:m="http://travelcompany.example.org/">
       <m:code>FT35ZBQ</m:code>
       <m:viewAt>
         http://travelcompany.example.org/reservations?code=FT35ZBQ
       </m:viewAt>
     </m:chargeReservationResponse>
 </env:Body>
</env:Envelope>"""

resp = libxml2dom.soap.parseString(response)
print "Method name:", resp.method.methodName
print "Parameter values:", resp.method.parameterValues
print "Fault:", resp.fault
print
print "Request parameters vs. response parameters:"
print req.method.parameters[0][0], resp.method.parameters[0]
print
assert resp.method.methodName == "chargeReservationResponse"
assert resp.method.parameterValues == [
    ("code", "FT35ZBQ"),
    ("viewAt", "http://travelcompany.example.org/reservations?code=FT35ZBQ")
    ]
assert resp.fault is None
assert req.method.parameters[0][0] == resp.method.parameters[0]

response2 = """<?xml version='1.0' encoding='iso-8859-1'?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope" >
 <env:Header>
    <t:transaction
       xmlns:t="http://thirdparty.example.org/transaction"
         env:encodingStyle="http://example.com/encoding"
          env:mustUnderstand="true">5</t:transaction>
 </env:Header>  
 <env:Body>
    <m:chargeReservationResponse 
       env:encodingStyle="http://www.w3.org/2003/05/soap-encoding"
           xmlns:rpc="http://www.w3.org/2003/05/soap-rpc"
             xmlns:m="http://travelcompany.example.org/">
       <rpc:result>m:status</rpc:result>
       <m:status>confirmed</m:status>
       <m:code>FT35ZBQ</m:code>
       <m:viewAt>
        http://travelcompany.example.org/reservations?code=FT35ZBQ
       </m:viewAt>
    </m:chargeReservationResponse>
 </env:Body>
</env:Envelope>"""

resp2 = libxml2dom.soap.parseString(response2)
print "Method name:", resp2.method.methodName
print "Parameter values:", resp2.method.parameterValues
print "Fault:", resp2.fault
print
print "Request parameters vs. response parameters:"
print req.method.parameters[0][0], resp2.method.parameters[2]
print
print "Response parameters:"
print resp.method.parameters[0], resp2.method.parameters[2]
print resp.method.parameters[1], resp2.method.parameters[3]
print
assert resp2.method.methodName == "chargeReservationResponse"
assert resp2.method.parameterValues == [
    ("result", "m:status"),
    ("status", "confirmed"),
    ("code", "FT35ZBQ"),
    ("viewAt", "http://travelcompany.example.org/reservations?code=FT35ZBQ")
    ]
assert resp2.fault is None
assert req.method.parameters[0][0] == resp2.method.parameters[2]
assert resp.method.parameters[0] == resp2.method.parameters[2]
assert resp.method.parameters[1] == resp2.method.parameters[3]

failed = """<?xml version='1.0' encoding='iso-8859-1'?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope"
            xmlns:rpc='http://www.w3.org/2003/05/soap-rpc'>
  <env:Body>
   <env:Fault>
     <env:Code>
       <env:Value>env:Sender</env:Value>
       <env:Subcode>
        <env:Value>rpc:BadArguments</env:Value>
       </env:Subcode>
     </env:Code>
     <env:Reason>
      <env:Text xml:lang="en-US">Processing error</env:Text>
      <env:Text xml:lang="cs">Chyba zpracování</env:Text>
     </env:Reason>
     <env:Detail>
      <e:myFaultDetails 
        xmlns:e="http://travelcompany.example.org/faults">
        <e:message>Name does not match card number</e:message>
        <e:errorcode>999</e:errorcode>
      </e:myFaultDetails>
     </env:Detail>
   </env:Fault>
 </env:Body>
</env:Envelope>"""

f = libxml2dom.soap.parseString(failed)
print "Fault code:", f.fault.code
assert f.method is None
assert f.fault.code == "env:Sender"
assert f.fault.subcode == "rpc:BadArguments"

# vim: tabstop=4 expandtab shiftwidth=4
