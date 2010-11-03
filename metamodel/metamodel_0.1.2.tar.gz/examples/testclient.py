from twisted.internet import reactor
from metamodel.datasources.twistedmm.client import MMClientDataSource
from metamodel import SubscribableModel

def print_model(model, spaces=1):
    print " "*spaces,"* "+model.name,"("+model.__class__.__name__+")"
    for child in model.getChildren():
        print_model(child, spaces+1)


class MyClient(MMClientDataSource):
    def clientConnected(self):
        root = self.getChildren()[0]
        print "DATA:"
        print_model(self)

client = MyClient()
client.port = 10110
client.server = '10.66.66.69'
client.active = True
reactor.run()

