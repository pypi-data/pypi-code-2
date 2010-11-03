from twisted.internet import reactor
from metamodel.datasources.twistedmm.server import MMServerDataSource
from metamodel.datasources.filesource import FileDataSource
from metamodel.datasources.restserver import MMRestServer
from metamodel.datasources.rsssource import RSSDataSource
#from metamodel.datasources.twistedmm.client import MMClientDataSource

from metamodel import SubscribableModel as Model
from metamodel import Property


class TestClass(Model):
    name = Property(str, 'name')
    testprop = Property(str, '')
    testprop2 = Property(str, '')



server = MMServerDataSource()
file = FileDataSource(file="serverdata.caf", name="data")
rsssource =file.new('RSSDataSource',url='https://aphro.site5.com/~doodoorg/tech/feed.php',name='name')
rsssource.delay = 60
rsssource.active = True
print file.getChildren()
server.addChild(file)
if not len(file.getChildren()):
    m = file.new('TestClass', name='node1', testprop='foo', testprop2='bla')
    file.addChild(m)
    m = file.new('TestClass', name='node2', testprop='bar', testprop2='stuff')
    file.addChild(m)

restserver = MMRestServer()
restserver.addChild(file)
restserver.addChild(rsssource)

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

restserver.port = 8000
restserver.active = True

reactor.run()
print "saving..."
file.save()

