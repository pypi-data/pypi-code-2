from twisted.internet import reactor
from metamodel.datasources.twistedmm.server import MMServerDataSource
from metamodel.datasources.filesource import FileDataSource
#from metamodel.datasources.twistedmm.client import MMClientDataSource


server = MMServerDataSource()
file = FileDataSource(file="serverdata.caf", name="data")
server.addChild(file)
print file.getChildren()

class CommandsServer(MMServerDataSource):
    def addChild(self, child):
        print " --> saving"
        print file.getChildren()
        print map(lambda s: s._datasource, file.getChildren())
        file.save()

commands = CommandsServer()
server.port = 10110
commands.port = 10113
server.active = True
commands.active = True
reactor.run()
print "saving..."
file.save()

