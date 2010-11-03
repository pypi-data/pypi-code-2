"""
Metamodel protocol 1 server
"""

import os

from twisted.internet.protocol import Factory
from twisted.internet import reactor

from twisted.internet.interfaces import IReactorSSL
try:
    from twisted.internet.ssl import DefaultOpenSSLContextFactory
except:
    pass # XXX no ssl support!

import metamodel
from metamodel import Property, File
from metamodel.datasources import DataSource
from metamodel.yamlserializer import SaveModel

from proto import MetamodelProtocol1
from proto import PC, DEL, ADD, INV
from guardian import InstanceGuardian

class MetamodelServerProtocol1(MetamodelProtocol1):
    # connection state
    transport = None
    factory = None
    def connectionMade(self):
        """ send current world state """
        self.transport.write("INIT:\n")
        self.factory.serializeModel(self.factory, self.transport.write,
                                        inst_mapping={self.factory: "DataSourceRoot"})
        self.transport.write("ENDINIT\n")
        # we have a client!
        self.factory._clients.append(self)
        self.state = 1 # XXX this shouldn't be set until client says ok.
        self.factory.state = 1

    def connectionLost(self, reason):
        """ connection to client lost """
        self.factory._clients.remove(self)

    def clientOK(self):
        """ client finished initialization """
        self.state = 1
        self.factory.state = 1

    # network message callbacks
    def setProperty(self, data, obj_uuid, name, val):
        self.factory.state = 2
        setattr(self.factory._instances[obj_uuid], name, val)
        self.sendToOthers(data+"\n")
        self.factory.state = 1

    def setReference(self, data, obj_uuid, name, val_uuid):
        self.factory.state = 2
        val = self.factory._instances[val_uuid]
        setattr(self.factory._instances[obj_uuid], name, val)
        self.sendToOthers(data+"\n")
        self.factory.state = 1

    def addChild(self, data, parent, child):
        if str(child.uuid) in self.factory._waitingparent:
            if isinstance(parent, DataSource):
                parent.own(child) # bad re-sourcing
            else:
                parent._datasource.own(child) # bad re-sourcing
        self.factory.state = 2
        parent.addChild(child)
        self.factory.state = 1
        self.sendToOthers(data+"\n")

    def delChild(self, data, parent, child):
        self.factory.state = 2
        parent.delChild(child)
        self.sendToOthers(data+"\n")
        self.factory.state = 1

    def invalidate(self, data, model):
        self.factory.state = 2
        model.invalidate()
        self.factory.state = 1
        self.sendToOthers(data+"\n")

    def newInstances(self, instdata, instances):
        self.factory.state = 2
        # instances already created at this point.
        self.sendToOthers("\nNEW\n"+instdata+"\nENDNEW\n")
        self.factory.state = 1


class MetamodelServerFactory(Factory):
    protocol = MetamodelServerProtocol1

    def serializeModel(self, model, userfunc=None, **kwargs):
        mapping={}
        if self.greedy:
            alldatasources = metamodel.meta._ChildInfo["DataSource"]
            for ds in alldatasources:
                mapping[ds] = "NetworkedDataSource"
        data = SaveModel(model, datasource=self, userfunc=userfunc, greedy=self.greedy, class_mapping=mapping, **kwargs)
        return data

    def sendPropertyChange(self, model, name, value):
        self.sendToAll(PC(model, name, value))

    def sendReferenceChange(self, model, name, value):
        value_uuid = str(value.uuid)
        if not value in self._instances:
            data = "NEW\n"+SaveModel(model, datasource=self, greedy=self.greedy)+"\nENDNEW\n"
            self.sendToAll(data)
        self.sendToAll(REF(model, name, value))

    def sendNew(self, instance):
        data = "NEW\n"+self.serializeModel(instance)+"\nENDNEW\n"
        self.sendToAll(data)

    def sendDelChild(self, parent, child):
        self.sendToAll(DEL(parent,child))

    def sendInvalidate(self, model):
        self.sendToAll(INV(model))

    def sendAddChild(self, parent, child):
        self.sendToAll(ADD(parent, child))

    def sendToAll(self, data):
        for client in self._clients:
            client.transport.write(data)


class ServerInstanceGuardian(InstanceGuardian):
    def addchild(self, child):
        print " - add foreign child",child
        self._datasource.add_foreign_child(child)
        if not self._datasource.state == 1:
            return
        self._datasource.sendAddChild(self._model, child)

    def delchild(self, child):
        if not self._datasource.state == 1:
            return
        self._datasource.sendDelChild(self._model, child)

    def invalidate(self):
        self._datasource.invalidate_foreign(self._model)
        if not self._datasource.state == 1:
            return
        self._datasource.sendInvalidate(self._model)


class MMServerDataSource(DataSource, MetamodelServerFactory):
    port = Property(int, 10110)
    active = Property(bool, False)
    connected = False
    greedy = Property(bool, True)
    key = File(["key"],"test/server.key")
    certificate = File(["crt"],"test/server.crt")

    def __init__(self, *args, **kwargs):
        self.state = 0
        active = None
        if "active" in kwargs:
            active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)
        self._clients = []
        self._instances = {}
        self._guardians = {}
        self._waitingparent = []
        self._proto = self # hack so we can use the same instance guardian as the client
        if not active == None:
            self.active = active
        self._instances[str(self.uuid)] = self

    # hook 'active' to activate the connection. note at the moment
    # all other properties must be already setup by the time the source
    # is activated.
    def setProperty(self, name, value):
        DataSource.setProperty(self, name, value)
        if name == "active" and value == True and not self.connected:
            try:
                if self.port == 10111 and os.path.exists(self.key) and os.path.exists(self.certificate):
                    self._ctx = DefaultOpenSSLContextFactory(self.key, self.certificate)
                    reactorssl = IReactorSSL(reactor)
                    reactorssl.listenSSL(self.port, self, self._ctx)
                else:
                    reactor.listenTCP(self.port, self)
                    print "listenTCP",self.port
                self.connected = True
            except:
                self.connected = False

    # hook up addChild and delChild to update the datasourceroot at
    # the same time
    def addChild(self, child):
        DataSource.addChild(self, child)
        self.add_foreign_child(child)
        if self.state == 1:
             self.sendAddChild(self, child)

    def delChild(self, child):
        DataSource.delChild(self, child)
        if self.state == 1:
             self.sendDelChild(self, child)

    # foreign childs addition and removal
    def add_foreign_child(self, node):
        node_uuid = str(node.uuid)
        if not node_uuid in self._instances:
            self.sendNew(node)
            self._instances[node_uuid] = node
            for child in node.getChildren():
                self.add_foreign_child(child)
            print "create guardian",node,str(node.uuid)
            self._guardians[node_uuid] = ServerInstanceGuardian(node, self)
            return True

    def invalidate_foreign(self, node):
        if not node._datasource == self:
            del self._instances[str(node.uuid)]
            del self._guardians[str(node.uuid)]

    # data source api
    def new(self, *args, **kwargs):
        if self._datasource:
            # transfer all nodes here to parent datasource
            inst = self._datasource.new(*args, **kwargs)
        else:
            inst = DataSource.new(self, *args, **kwargs)
        self._instances[str(inst.uuid)] = inst
        self._guardians[str(inst.uuid)] = ServerInstanceGuardian(inst, self)
        self._waitingparent.append(str(inst.uuid))
        if self.state == 1:
            self.sendNew(inst)
        return inst

    def invalidate(self, node):
        del self._instances[str(node.uuid)]
        del self._guardians[str(node.uuid)]
        DataSource.invalidate(self, node)

    buids = ["NetworkedModel"]
    builtby = ["DataSource"]


