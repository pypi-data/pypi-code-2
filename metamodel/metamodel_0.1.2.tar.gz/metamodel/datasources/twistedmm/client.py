from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor

from twisted.internet.interfaces import IReactorSSL
from twisted.internet.ssl import ClientContextFactory

from metamodel.properties import Property
from metamodel.datasources import DataSource

from proto import MetamodelProtocol1
from guardian import InstanceGuardian


class MetamodelClientProtocol1(MetamodelProtocol1):
    """
    twistedmm client protocol
    """
    # responses to arrived messages
    def clientOK(self):
        # make messages coming to server uuid go to ourselves instead.
        self.factory._instances[str(self.server_uuid)] = self.factory
        self.factory.clientConnected()

    def setProperty(self, data, obj_uuid, name, val):
        self.state = 2
        setattr(self.factory._instances[obj_uuid], name, val)
        self.state = 1

    def setReference(self, data, obj_uuid, name, val_uuid):
        self.state = 2
        val = self.factory._instances[val_uuid]
        setattr(self.factory._instances[obj_uuid], name, val)
        self.state = 1

    def addChild(self, data, parent, child):
        self.state = 2
        parent.addChild(child)
        self.state = 1

    def delChild(self, data, parent, child):
        self.state = 2
        parent.delChild(child)
        self.state = 1

    def invalidate(self, data, model):
        self.state = 2
        model.invalidate()
        self.state = 1


class MetamodelClientFactory(ReconnectingClientFactory):
    """
    twistedmm client factory
    """
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def clientConnected(self):
        pass

    def buildProtocol(self, addr):
        self.resetDelay()
        proto = MetamodelClientProtocol1()
        proto.factory = self
        self._proto = proto
        return proto

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)


class MMClientDataSource(DataSource, MetamodelClientFactory):
    """
    twistedmm client datasource
    """
    server = Property(str,'localhost')
    port = Property(int, 10110)
    active = Property(bool, False)
    connected = False

    def __init__(self, *args, **kwargs):
        self._instances = {}
        self._proto = None
        self._invalidating = False
        active = None
        if "active" in kwargs:
            active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)
        if not active == None:
            self.active = active

    def clientConnected(self):
        self.post('connected')

    def getChildrenToPersist(self):
        return []

    def setProperty(self, name, value):
        DataSource.setProperty(self, name, value)
        if name == "active" and value == True and not self.connected:
            if self.port == 10111:
                self._ctx = ClientContextFactory()
                reactorssl = IReactorSSL(reactor)
                reactorssl.connectSSL(self.server, self.port, self, self._ctx)
            else:
                reactor.connectTCP(self.server, self.port, self)
            self.connected = True

    def new(self,*args,**kwargs):
        inst = DataSource.new(self, *args, **kwargs)
        self.accept(inst)
        return inst

    def release(self, inst):
        self._proto.server_node.delChild(inst)
        DataSource.release(self, inst)

    def accept(self, inst):
        DataSource.accept(self, inst)
        InstanceGuardian(inst, self)
        self._instances[str(inst.uuid)] = inst
        if self._proto and self._proto.state == 1:
            self._proto.sendNew(inst)

    def addChild(self, child):
        DataSource.addChild(self, child)

        if child._datasource == self and self._proto.state == 1:
            self._proto.server_node.addChild(child)

    def delChild(self, child):
        DataSource.delChild(self, child)

        if not self._invalidating and child._datasource == self and self._proto.state == 1:
            self._proto.server_node.delChild(child)

    def invalidate(self, node=None):
        self._invalidating = 1
        DataSource.invalidate(self, node)
        self._invalidating = 0

    builtby = ["DataSource"]

