from twisted.internet.protocol import Protocol
from metamodel.yamlserializer import LoadModel, SaveModel, LoadValue, SaveValue
import sys

from model import NetworkedModel
from metamodel import dynamicmeta


#############################################################
# Protocol message composition

def PC(model, name, value):
    return "PC:"+str(model.uuid)+":"+name+":"+SaveValue(value)+"\n"

def REF(model, name, value):
    if value:
        return "REF:"+str(model.uuid)+":"+name+":"+str(value.uuid)+"\n"

def DEL(parent, child):
    return "DELCHILD:"+str(parent.uuid)+":"+str(child.uuid)+"\n"

def ADD(parent, child):
    return "ADDCHILD:"+str(parent.uuid)+":"+str(child.uuid)+"\n"

def INV(model):
    return "INVALIDATE:"+str(model.uuid)+"\n"


#############################################################
# Protocol Class

class MetamodelProtocol1(Protocol):
    lines= ""
    receiving = 0
    receiving_line = False
    state = 0
    transport = None
    factory = None

    def dataReceived(self, data):
        if self.receiving_line:
            data = self.receiving_data + data
            self.receiving_line = False
        lines = data.split("\n")
        for idx,line in enumerate(lines):
            if idx == len(lines)-1:
                if not line:
                    # XXX stupid
                    self.lineReceived(line, lastline=True)
                else:
                    self.receiving_line = True
                    self.receiving_data = line
            else:
                self.lineReceived(line)

    def sendNamespaces(self):
        print " * send ontologies"
        self.transport.write("ONTOLOGIES\n")
        data = SaveModel(dynamicmeta.Registry, userfunc=self.transport.write)
        self.transport.write("\nENDONTOLOGIES\n")

    def loadNamespaces(self, data):
        self.factory.state = 1
        ontologies = LoadModel(data, "InstanceRegistryModel")[0].getChildren()
        self.factory.state = 2
        for ont in ontologies:
            print " * load Namespace:",ont.name
            dynamicmeta.Registry.addChild(ont)

    def lineReceived(self, data, lastline=False):
        if self.receiving == 1:
            if data.startswith("ENDNEW"):
                instdata = self.lines
                self.receiving = 0
                self.lines = ""
                self.state = 2
                self.factory.state = 2
                instances = LoadModel(instdata, datasource=self.factory)
                for inst in instances:
                    print " * new:",inst.name,inst.uuid
                self.factory.state = 1
                self.state = 1
                self.newInstances(instdata, instances)
            else:
                if lastline:
                    self.lines += data
                else:
                    self.lines += data+"\n"
        elif self.receiving == 2:
            if data.startswith("ENDONTOLOGIES"):
                print " * ontologies received"
                instdata = self.lines
                self.receiving = 0
                self.lines = ""
                self.state = 2
                self.factory.state = 2
                self.loadNamespaces(instdata)
                self.factory.state = 1
                self.state = 1
            else:
                if lastline:
                    self.lines += data
                else:
                    self.lines += data+"\n"
        elif self.receiving == 3:
            if data.startswith("ENDINIT"):
                self.factory._proto = self
                instdata = self.lines
                self.receiving = 0
                self.lines = ""
                self.state = 2
                self.factory.state = 2
                a = LoadModel(instdata,'DataSourceRoot', datasource=self.factory)[0]
                self.server_uuid = a.uuid
                self.server_node = a
                for child in a.getChildren():
                     self.factory.addChild(child)
                self.factory.state = 1
                self.state = 1
                self.sendNamespaces()
                self.clientOK()
                self.transport.write("INITOK\n")
            else:
                if lastline:
                    self.lines += data
                else:
                    self.lines += data+"\n"
        elif data.startswith("NEW"):
            self.receiving = 1
        elif data.startswith("INIT:"):
            self.receiving = 3
        elif data.startswith("ONTOLOGIES"):
            self.receiving = 2
        elif data.startswith("INITOK"):
            self.clientOK()
        elif data.startswith("PC:"):
            vals = data.split(":",3)
            obj_uuid = vals[1]
            name = vals[2]
            val = LoadValue(vals[3])
            self.setProperty(data, obj_uuid, name, val)
        elif data.startswith("REF:"):
            vals = data.split(":",3)
            obj_uuid = vals[1]
            name = vals[2]
            val_uuid = vals[3]
            self.setReference(data, obj_uuid, name, val_uuid)
        elif data.startswith("ADDCHILD:"):
            vals = data.split(":")
            parent_uuid = vals[1]
            child_uuid = vals[2]
            parent = self.factory._instances[parent_uuid]
            child = self.factory._instances[child_uuid]
            print " * addchild:",parent_uuid,child_uuid
            self.addChild(data, parent, child)
        elif data.startswith("INVALIDATE:"):
            vals = data.split(":")
            model_uuid = vals[1]
            model = self.factory._instances[model_uuid]
            print " * invalidate:",model_uuid
            self.invalidate(data, model)
        elif data.startswith("DELCHILD:"):
            vals = data.split(":")
            parent_uuid = vals[1]
            child_uuid = vals[2]
            parent = self.factory._instances[parent_uuid]
            child = self.factory._instances[child_uuid]
            print " * delchild:",parent_uuid,child_uuid
            self.delChild(data, parent, child)
        elif data.startswith("GET") and "HTTP" in data:
            # hack so you can see the data structures from a web browser.
            self.transport.loseConnection()

    # message callbacks, to be implemented by subclasses
    def clientOK(self):
        pass

    def setProperty(self, data, obj_uuid, name, val):
        pass

    def setReference(self, data, obj_uuid, name, val_uuid):
        pass

    def addChild(self, data, parent, child):
        pass

    def delChild(self, data, parent, child):
        pass

    def invalidate(self, data, model):
        pass

    def newInstances(self, instdata, instances):
        pass

    def preNewInstances(self, instdata):
        pass

    # sending functions
    def sendPropertyChange(self, model, name, value):
        self.transport.write(PC(model, name, value))

    def sendReferenceChange(self, model, name, value):
        value_uuid = str(value.uuid)
        if not value_uuid in self.factory._instances:
            data = SaveModel(value, datasource=self.factory)
            self.transport.write("NEW\n"+data+"\nENDNEW\n")
            self.factory._instances[value_uuid] = value
        self.transport.write(REF(model, name, value))

    def sendNew(self, instance):
        data = SaveModel(instance, datasource=self.factory)
        self.transport.write("NEW\n"+data+"\nENDNEW\n")

    def sendDelChild(self, parent, child):
        self.transport.write(DEL(parent,child))

    def sendInvalidate(self, model):
        self.transport.write(INV(model))

    def sendAddChild(self, parent, child):
        self.transport.write(ADD(parent, child))

    def sendToOthers(self, data):
        for client in self.factory._clients:
            if not client == self:
                client.transport.write(data)


