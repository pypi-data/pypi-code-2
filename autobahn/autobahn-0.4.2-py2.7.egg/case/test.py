import random

DynamicCases = []


def __init__(self):
   self.ran = random.random()

def getPayload(self):
   return self.PAYLOAD, self.ran

for i in xrange(0, 4):
   C = type("Case6_9_%d" % i,
             (object,),
             {"PAYLOAD": "\xED\xA0\x80" * i,
              "__init__": __init__,
              "getPayload": getPayload})
   DynamicCases.append(C)

for C in DynamicCases:
   c = C()
   print c.__class__
   print c.PAYLOAD
   print c.getPayload()
   c = C()
   print c.__class__
   print c.PAYLOAD
   print c.getPayload()
