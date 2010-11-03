"""
An xmpp datasource.
"""

from collections import defaultdict

from metamodel import Property, Password
from metamodel.basemodel import SubscribableModel

from metamodel.datasources import DataSource

from twisted.words.protocols.jabber import client, jid, xmlstream
from twisted.words.xish import domish

from twisted.internet import reactor

# for tls xmpp connections:
from twisted.internet.interfaces import IReactorSSL
from twisted.internet.ssl import ClientContextFactory

from wokkel import pubsub, xmppim, disco, subprotocols
import uuid

# xmpp model
class XmppRosterItem(SubscribableModel):
    """
    A roster item for an xmpp connection.
    """
    name = Property(str, "a contact")
    jid = Property(str, ro=True)
    available = Property(bool, False, ro=True)
    subscriptionTo = Property(bool, False, ro=True)
    subscriptionFrom = Property(bool, False, ro=True)
    ask = Property(bool, False, ro=True)

class XmppContactsModel(SubscribableModel):
    """
    A contacts list for an xmpp connection.
    """
    name = Property(str, "contacts")

class XmppDiscoModel(SubscribableModel):
    """
    Discovery nodes.
    """
    name = Property(str, "disco")

class XmppPubsubItem(SubscribableModel):
    """
    A collection in a pubsub tree.
    """
    node = Property(str, "node")
    name = Property(str, "name")
    id = Property(str, "id")
    content = Property(str, "content")

class ServiceInfoNode(SubscribableModel):
    """
    An item in a pubsub tree.
    """
    name = Property(str, "disco")
    id = Property(str, "id", ro=True)
    node = Property(str, "disco", ro=True)
    content = Property(str, "")
    body = Property(str, "", ro=True)
    type = Property(str, "", ro=True)
    owner = Property(bool, True, ro=True)
    published = Property(bool, False)
    subscribed = Property(bool, False)
    category = Property(str, "", ro=True)

    builds = ["ServiceInfoNode"]

# xmpp service datasource.
# this is really just intended for pubsub, but used for other services atm.
class XmppService(DataSource):
    """
    An xmpp service.
    """
    def __init__(self, *args, **kwargs):
        DataSource.__init__(self, *args, **kwargs)

    def new(self, clsname, instance_uuid=None, *args, **kwargs):
        inst = DataSource.new(self, clsname, instance_uuid=instance_uuid, *args, **kwargs)
        if inst.__class__ == ServiceInfoNode and inst.published == False:
            PublishGuardian(inst)
        self._datasource._pubsubnodes[self.jid].append(inst)
        return inst

    def delete_done(self, stanza, node):
        self._datasource._pubsubnodes[self.jid].remove(node)
        node.invalidate(True)

    def invalidate(self, node):
        if isinstance(node, ServiceInfoNode):
            if not "!" in node.node:
                d = self._datasource.pubsub.deleteNode(jid.JID(self.name), node.node)
                d.addCallback(self.delete_done, node)
            # XXX how to delete items?
        else:
            node.invalidate(True)

    name = Property(str, "disco")
    jid = Property(str, "jid", ro=True)
    owner = Property(bool, False, ro=True)


# publish guardian. waits on new nodes for publishing.
class PublishGuardian(object):
    """
    Class to guard for publishing.
    """
    def __init__(self, model):
        model.subscribe(self)
        self._model = model

    def propertychange(self, name, value):
        if name == "published" and value == True:
            self._model.unsubscribe(self)
            self.publish()

    def publish(self):
        url = self._model._datasource.name
        node = self._model.getParents()[0].node
        content = self._model.content
        if content:
            item = domish.Element((None, 'item'))
            item.addRawXml(content)
            d = self._model._datasource._datasource.pubsub.publish(jid.JID(url), node, [item])
            d.addCallback(self._publish_done, node)
        else:
            node = node+"/"+self._model.name
            d = self._model._datasource._datasource.pubsub.createNode(jid.JID(url), node)
            d.addCallback(self._new_done, node)

    def _new_done(self, item, nodepath):
        self._model.node = nodepath
        self._model.unsubscribe(self)

    def _publish_done(self, item, nodepath):
        self._model.node = nodepath+"!UNKNOWN"
        self._model.name = self._model.content
        self._model.unsubscribe(self)


# node controller. subscribes to the model for changes, fills it in with
# discovery information.
class ServiceInfo(object):
    def __init__(self, model, name, protos, node="", url=""):
        self.model = model
        self._name = name
        self._url = url
        self._node = node
        self._disco = protos[0]
        self._pubsub = protos[1]
        self._primed = False
        self._type = ""
        self.model.subscribe(self)
        if not url:
            self._url = self._name
        else:
            self._url = url
        self._nodes = {}

        # XXX nasty hack to do lazy expansion
        self.model._getChildren = model.getChildren
        self.model.getChildren = self.getChildChildren

    # subscription
    def propertychange(self, name, value):
        if name == "subscribed" and value == True:
            servicejid = self.model._datasource.jid
            nodeid = self.model.node
            selfjid = self.model._datasource._datasource.jid
            d = self._pubsub.subscribe(jid.JID(servicejid), nodeid, jid.JID(selfjid))
            d.addErrback(self.subscribe_failed)
            d.addCallback(self.subscribe_succeeded)

    def subscribe_failed(self, *args):
        self.model.subscribed = False

    def subscribe_ok(self, *args):
        self.model.subscribed = True

    # invalidate model
    def invalidate(self):
        self.model.unsubscribe(self)
        self.model = False

    def getChildChildren(self):
        self.model.getChildren = self.model._getChildren
        self.prime()
        return self.model.getChildren()

    # send initial discovery information request
    def prime(self):
        if self._primed:
            return
        if "!" in self._node:
            return
        d = self._disco.requestInfo(jid.JID(self._url), self._node)
        
        d.addCallback(self.discoInfoResponse)
        #d.addErrback(self.discoInfoError)
        self._primed = True
        self.extinfo = ""
        return d

    def discoInfoError(self, failure):
        print "discoInfoError", failure, dir(failure)

    # get initial information, and request items
    def discoInfoResponse(self, items):
        for item in items:
            if item.name == "identity":
                self._category = item["category"]
                atype = str(item["type"])
                if self._type:
                    self._type += ","+atype
                else:
                    self._type += atype
                #try:
                #    name=item["name"]
                #except KeyError:
                #    name=item["category"]
            if item.name == "feature":
                #self.model.addChild(self.model.new(XmppDiscoFeature,name=item["var"]))
                pass
        d = self._disco.requestItems(jid.JID(self._url), self._node)
        d.addCallback(self.discoItemsResponse)
        #d.addErrback(self.discoItemsError)

    def discoItemsError(self, failure):
        print "discoItemsError", failure

    # get disco items, and request pubsub items if its a leaf
    def discoItemsResponse(self, items):
        # separate services from pubsub nodes, create items for both
        for item in items:
            protos = [self._disco, self._pubsub]
            atype = self._type
            try:
                if "!" in item["node"]:
                    atype="item"
                model = self.model.new(ServiceInfoNode,
                                    name=item["name"],
                                    node=item["node"],
                                    id=item["name"],
                                    published=True,
                                    type=atype,
                                    category=self._category)
                self.model.addChild(model)
                service = ServiceInfo(model, item["name"], protos,
                                      item["node"], self._url)
                self._nodes[item["name"]] = service
            except:
                model = self.model.new(XmppService,
                                       jid=item["jid"],
                                       name=item["jid"])
                self.model.addChild(model)
                s = ServiceInfo(model, item["jid"], protos)
        if "leaf" in self._type: # "leaf": XXX pubsub get items doesnt work as expected
            d = self._pubsub.items(jid.JID(self._url), self._node)
            d.addCallback(self.pubsubItemsResponse)
            d.addErrback(self.pubsubItemsError)


    def pubsubItemsError(self, failure):
        elmt = failure.value.getElement()
        if str(elmt["code"]) == "401" and str(elmt["type"]) == "auth":
            self.model.owner = False

    # get pubsub items
    def pubsubItemsResponse(self, items):
        # create subservices
        for item in items:
            body = item.addContent("")
            if body.strip():
                self._nodes[item["id"]].model.content = body
                self._nodes[item["id"]].model.name = body
            else:
                self._nodes[item["id"]].model.name = item.toXml()
            self._nodes[item["id"]].model.body = item.toXml()


# data source
class XmppDataSource(DataSource):
    active = Property(bool, False)
    usessl = Property(bool, False)
    name = Property(str, "an xmpp data source")
    server = Property(str, "delirium")
    password = Password()
    jid = Property(str,"caedes@delirium/CA")
    port = Property(int, 5222)
    def __init__(self, *args, **kwargs):
        self._connected = False

        active = None
        if "active" in kwargs:
            active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)

        # following nodes won't be persisted, but always get the same uuid,
        # relative to this one.
        self.contactsmodel = XmppContactsModel(uuid.uuid5(self.uuid, 'contacts'), self)
        self.discomodel = XmppDiscoModel(uuid.uuid5(self.uuid, 'disco'), self)
        self.received = XmppDiscoModel(uuid.uuid5(self.uuid, 'received'),
                                                       self,
                                                       name="received")
        self.addChild(self.contactsmodel)
        self.addChild(self.discomodel)
        self.addChild(self.received)

        # some lists to keep track of things we have seen already
        self._contacts = {}
        self._pubsubnodes = defaultdict(list)
        # hook up on_uuid_set so we can update children uuids if uuid changes.
        if not active == None:
            self.active = active
        self.on_uuid_set = self._on_uuid_set

    # DataSource operations
    def _on_uuid_set(self):
        self.contactsmodel.uuid = uuid.uuid5(self.uuid, 'contacts')
        self.discomodel.uuid = uuid.uuid5(self.uuid, 'disco')
        self.received.uuid = uuid.uuid5(self.uuid, 'received')

    # Activate
    def setProperty(self, name, value):
        SubscribableModel.setProperty(self, name, value)
        if name == "active":
            if value == False and self._connected:
                self.disconnectXmpp()
            elif value == True and not self._connected:
                self.connectXmpp()

    # Connect / Disconnect
    def disconnectXmpp(self):
        self._connected = False
        self.xmlstream.sendFooter()
        self._proto.disconnect()
        self._fact.stopTrying() # is this the best way to stop the factory?
        self._proto = None
        self._fact = None

    def connectXmpp(self):
        """
        Call this function to connect.
        """
        my_jid = jid.JID(self.jid)

        factory = client.basicClientFactory(my_jid, self.password)
        self._fact = factory
        if self.usessl:
            self._ctx = ClientContextFactory()
            reactorssl = IReactorSSL(reactor)
            self._proto = reactorssl.connectSSL(self.server, self.port, self._fact, self._ctx)
        else:
            self._proto = reactor.connectTCP(self.server, self.port, self._fact)
        self.collection = subprotocols.StreamManager(factory)
        factory.addBootstrap('//event/stream/authd', self.authd)
        factory.addBootstrap(xmlstream.INIT_FAILED_EVENT, self.init_failed)
        factory.addBootstrap(xmlstream.STREAM_END_EVENT, self.stream_end)
        self._connected = True

    def init_failed(self, *args):
        pass

    def stream_end(self, *args):
        self.contactsmodel.purgeChildren()
        self.discomodel.purgeChildren()
        self._contacts = {}
        self._pubsubnodes = defaultdict(list)
        if self._connected:
            self._connected = False

    def authd(self, xs):
        """
        This function will be called on auth.
        """
        self.xmlstream = xs

        # roster protocol
        self.rprotocol = xmppim.RosterClientProtocol()
        self.rprotocol.setHandlerParent(self.collection)
        d = self.rprotocol.getRoster()
        d.addCallback(self.rosterArrived)

        # presence
        self.pprotocol = xmppim.PresenceClientProtocol()
        self.pprotocol.setHandlerParent(self.collection)
        self.pprotocol.availableReceived = self.availableReceived
        self.pprotocol.unavailableReceived = self.unavailableReceived
        self.sendPresence()

        # pubsub
        self.pubsub = pubsub.PubSubClient()
        self.pubsub.setHandlerParent(self.collection)
        self.pubsub.itemsReceived = self.itemsReceived
        self.pubsub.deleteReceived = self.deleteReceived
        self.pubsub.purgeReceived = self.purgeReceived
        self.pubsub.nodes = {}

        # disco
        self.disco = disco.DiscoClientProtocol()
        self.disco.setHandlerParent(self.collection)

        self.createServiceModel(self.disco, self.pubsub)

        self.discomodel.getChildren() # dummy getchildren to trigger discovery

    def createServiceModel(self, disco, pubsub):
        service = ServiceInfo(self.discomodel, self.server, [disco, pubsub])

    # PubSub events
    def processItems(self, items, parentnode, nodeIdentifier):
        for item in items:
            node = self.discomodel.new(ServiceInfoNode,
                                       name=item["id"],
                                       node = nodeIdentifier+"!"+item["id"],
                                       id=item["id"],
                                       published=True,
                                       body=item.toXml())
            body = item.addContent("")
            if body.strip():
                node.content = body
                node.name = body
            parentnode.addChild(node)
            self.received.addChild(node)

    def itemsReceived(self, event):
        servicejid = event.sender.full()
        if servicejid in self._pubsubnodes:
            parentnodes = filter(lambda s: s.node == event.nodeIdentifier, 
                                           self._pubsubnodes[servicejid])
            if parentnodes:
                 self.processItems(event.items, parentnodes[0], event.nodeIdentifier)
            # else: dont throw away...  XXX
        # else: dont throw away...  XXX

    def deleteReceived(self, event):
        servicejid = sender.full()
        print "DELETE RECEIVED!", servicejid
        if servicejid in self._pubsubnodes:
            nodes = filter(lambda s: s.node == event.nodeIdentifier,
                                self._pubsubnodes[servicejid])
            for node in nodes:
                self._pubsubnodes[servicejid].remove(node)
                self._pubsubnodes[servicejid].invalidate(True)

    def purgeReceived(self, event):
        print "purge", event

    # Presence Events
    def availableReceived(self, entity, show=None, statuses=None, priority=0):
        userjid = entity.userhost()
        if not userjid in self._contacts:
            rosteritem = self.contactsmodel.new(XmppRosterItem,
                                                 name=entity.userhost(),
                                                 jid=entity.full())
            self._contacts[userjid] = rosteritem
            self.contactsmodel.addChild(rosteritem)
        self._contacts[userjid].available = True

    def unavailableReceived(self, entity, statuses=None):
        if not entity.userhost() in self._contacts:
            return
        self._contacts[entity.userhost()].available = False

    def rosterArrived(self, roster):
        for item in roster.values():
            jid = item.jid.full()
            userjid = item.jid.userhost()
            if item.name:
                name = item.name
            else:
                name = jid
            if not userjid in self._contacts:
                rosteritem = self.contactsmodel.new(XmppRosterItem,
                                                name=userjid,
                                                jid=jid)
                self._contacts[userjid] = rosteritem
                self.contactsmodel.addChild(rosteritem)
            else:
                rosteritem = self._contacts[userjid]
            rosteritem.subscriptionTo = item.subscriptionTo
            rosteritem.subscriptionFrom = item.subscriptionFrom
            rosteritem.ask = item.ask

    def sendPresence(self):
        pres = xmppim.Presence()
        self.pprotocol.send(pres)

    builtby = ["DataSource"]
