import sys
from twisted.internet import reactor
from metamodel.datasources.twistedmm.server import MMServerDataSource
#from metamodel.datasources.twistedmm.client import MMClientDataSource

server = MMServerDataSource()
print sys.argv
if len(sys.argv) > 1:
    server.port = int(sys.argv[1])
else:
    server.port = 10110
server.active = True

#reactor.listenTCP(8007, MetamodelServerFactory())

reactor.run()


