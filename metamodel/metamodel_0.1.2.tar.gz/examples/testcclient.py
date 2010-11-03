from twisted.internet import reactor
from metamodel.datasources.twistedmm.client import MMClientDataSource
from metamodel import SubscribableModel

class MyClient(MMClientDataSource):
    def clientConnected(self):
        self.addChild(self.new(SubscribableModel))

client = MyClient()
client.port = 10113
client.server = 'localhost'
client.active = True
reactor.run()


