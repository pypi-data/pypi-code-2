from twisted.internet.protocol import Protocol

import os
import uuid
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
from metamodel.meta import ClassRegistry
from metamodel.dictserializer import find_uuid

import simplejson

class MetamodelRestProtocol(Protocol):
    # connection state
    transport = None
    factory = None

    def dataReceived(self, data):
        split_data = data.split("\n")
        idx = split_data.index('\r')
        data = "\n".join(split_data[idx+1:])
        first_line_split = split_data[0].split(" ")
        command = first_line_split[0].upper()
        url = first_line_split[1].strip()
        if command == "GET":
            self.getReceived(url, data)
        elif command == "PUT":
            self.putReceived(url, data)
        elif command == "POST":
            self.postReceived(url, data)
        elif command == "DELETE":
            self.deleteReceived(url, data)
        self.transport.loseConnection()

    def putReceived(self, url, data):
        model = self.getModelFromUrl(url)
        data = simplejson.loads(data)
        for key, val in data.iteritems():
            if isinstance(val, str):
                val = str(val)
            setattr(model, str(key), val)
        print " * put received",data
    def postReceived(self, url, data):
        model = self.getModelFromUrl(url)
        data = simplejson.loads(data)
        print data
        new_model = model.new(str(data['mm']))
        print new_model
        for key, val in data.iteritems():
            if key == 'mm':
                continue
            if new_model.trait(key)._reference:
                val = find_uuid(uuid.UUID(val)) 
            elif isinstance(val, str):
                val = str(val)
            setattr(new_model, str(key), val)
        model.addChild(new_model)
        print " * post received"
    def deleteReceived(self, url, data):
        print " * delete received",url
        model = self.getModelFromUrl(url)
        model.invalidate()
    def getReceived(self, url, data):
        if url == "/schema/":
            class_name = "MetaModel"
            acls = ClassRegistry[class_name]
            data = self.serializeNodeList(acls.get_instances())
        elif url.startswith("/classes/"):
            class_name = url.split("/")[2]
            acls = ClassRegistry[class_name]
            if url.endswith("/"):
                data = self.serializeNodeChildren(acls._model)
            else:
                data = self.serializeNodeProperties(acls._model)
        elif url.startswith("/instances/"):
            class_name = url.split("/")[2]
            acls = ClassRegistry[class_name]
            data = self.serializeNodeList(acls.get_instances())
        else:
            print url
            model = self.getModelFromUrl(url)
            print model
            if url.endswith('/'):
                data = self.serializeNodeChildren(model)
            else:
                data = self.serializeNodeProperties(model)
        self.transport.write("HTTP/1.0 200 Found\n")
        self.transport.write("Content-Type: text/json; charset=UTF-8\n\n")

        self.transport.write(data)
    def getModelFromUrl(self, url):
        schema = False
        if url.startswith('/schema/'):
            schema = True
            url = url[8:]
        model = self.factory.getFromUrl(url)
        if schema:
            model = model._model
        return model
    def serializeNodeProperties(self, model):
        data_dict = {}
        data_dict['uuid'] = str(model.uuid)
        for prop in model.properties:
            if model.trait(prop)._reference:
                child = getattr(model, prop)
                if child:
                    data_dict[prop] = str(child.uuid)
            else:
                data_dict[prop] = getattr(model, prop)
        data_dict['name'] = model.name
        data_dict['mm'] = model.__class__.__name__
        json_str = simplejson.dumps(data_dict)
        return json_str

    def serializeNodeChildren(self, model):
        return self.serializeNodeList(model.getChildren())

    def serializeNodeList(self, nodelist):
        data_list = []
        for node in nodelist:
            data_dict = {}
            data_dict['uuid'] = str(node.uuid)
            for prop in node.properties:
                print node
                val = getattr(node, prop)
                if node.trait(prop)._reference:
                    if val:
                        val = str(val.uuid)
                if not val == None:
                    data_dict[prop] = val

            data_dict['name'] = node.name
            data_dict['mm'] = node.__class__.__name__
            data_list.append(data_dict)
        try:
            json_str = simplejson.dumps(data_list)
        except:
            print "PRobLEMS SERIALIZING"+str(data_list)
        return json_str

    def connectionMade(self):
        """ send current world state """
        # we have a client!
        self.factory._clients.append(self)

    def connectionLost(self, reason):
        """ connection to client lost """
        self.factory._clients.remove(self)



class MetamodelRestServerFactory(Factory):
    protocol = MetamodelRestProtocol



class MMRestServer(DataSource, MetamodelRestServerFactory):
    port = Property(int, 8000)
    active = Property(bool, False)
    connected = False
    key = File(["key"],"test/server.key")
    certificate = File(["crt"],"test/server.crt")

    def __init__(self, *args, **kwargs):
        self.state = 0
        active = None
        if "active" in kwargs:
            active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)
        self._clients = []
        self._proto = self # hack so we can use the same instance guardian as the client
        if not active == None:
            self.active = active

    # hook 'active' to activate the connection. note at the moment
    # all other properties must be already setup by the time the source
    # is activated.
    def setProperty(self, name, value):
        DataSource.setProperty(self, name, value)
        if name == "active" and value == True and not self.connected:
            try:
                if self.port == 8001 and os.path.exists(self.key) and os.path.exists(self.certificate):
                    self._ctx = DefaultOpenSSLContextFactory(self.key, self.certificate)
                    reactorssl = IReactorSSL(reactor)
                    reactorssl.listenSSL(self.port, self, self._ctx)
                else:
                    reactor.listenTCP(self.port, self)
                    print "listenTCP",self.port
                self.connected = True
            except:
                self.connected = False


    buids = ["NetworkedModel"]
    builtby = ["DataSource"]





