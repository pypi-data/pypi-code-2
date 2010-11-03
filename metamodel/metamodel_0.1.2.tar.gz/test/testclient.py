import sys
from twisted.internet import reactor
from metamodel.datasources.twistedmm.client import MMClientDataSource

client = MMClientDataSource()

if len(sys.argv) > 2:
    client.port = int(sys.argv[2])
else:
    client.port = 10110

if len(sys.argv) > 1:
    client.server = sys.argv[1]
else:
    client.server = 'localhost'

client.active = True
reactor.run()


