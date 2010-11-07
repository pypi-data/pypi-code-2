"""
Consuming from RabbitMQ -- :class:`RabbitHandler`
-------------------------------------------------
.. autoclass:: RabbitHandler
   :show-inheritance:

Publishing to RabbitMQ -- :class:`RabbitQueue`
----------------------------------------------
.. autoclass:: RabbitQueue
   :show-inheritance:
"""
__all__ = ['RabbitQueue', 'RabbitHandler']

from ordf.handler import Handler, HandlerPlugin
from ordf.graph import Graph, _Graph
from ordf.namespace import UUID
from ordf.term import URIRef
from carrot.messaging import Consumer, Publisher
from carrot.connection import BrokerConnection

from StringIO import StringIO
from threading import Thread
from logging import getLogger
from traceback import format_exc
from time import sleep

class _Rabbit(object):
    def __init__(self, storage=None, **kw):
        if isinstance(storage, basestring):
            kw.update(eval(storage))
        elif storage:
            kw.update(storage)
        self.__rabbit_kw__ = kw
    @property
    def connection(self):
        return BrokerConnection(**self.__rabbit_kw__)

class RabbitQueue(HandlerPlugin, _Rabbit):
    """
    Publisher of graps to the queueing system. This is a subclass of
    :class:`ordf.handler.HandlerPlugin` suitable to be registered as a
    reader. Any arguments are passed through to the connection 
    constructor :class:`carrot.connection.BrokerConnection` .

    .. automethod:: connect
    """
    def __init__(self, *av, **kw):
        super(RabbitQueue, self).__init__(*av, **kw)
        self.publisher = None
        self.connected = False

    def connect(self, **kw):
        """
        Parameters are interpreted as in :meth:`RabbitHandler.connect`
        though clearly machinery is set up for publishing data rather than
        starting threads to process incoming data. There is therefore no
        need for a **queue** keyword argument.

        :param exchange: highly recommended, defaults to "ordf"
        """
        kw.setdefault("exchange", "ordf")
        kw.setdefault("exchange_type", "fanout")
        kwa = kw.copy()
        kwa["exchange"] = kw["exchange"]
        kwa["exchange_type"] = "fanout"
        self.log = getLogger(self.__class__.__name__ + "/" + kwa["exchange"])
        self.log.info("connected")
        self.publisher = Publisher(connection=self.connection, **kwa)
        self.connected = True

    def put(self, graph):
        subgraphs = []
        if isinstance(graph, _Graph):
            contexts = [graph]
        else:
            contexts = graph.contexts()
        for ctx in contexts:
            self.log.debug("send %s" % (ctx.identifier,))
            subgraphs.append((ctx.identifier, unicode(ctx.serialize(), "utf-8")))
        self.publisher.send(subgraphs)

class RabbitHandler(Handler, _Rabbit):
    """
    This *Handler* listens to a RabbitMQ server for graphs and changesets.
    When it receives one, it is injected via :meth:`put` . As with the super-class
    read and write back-ends may be registered and the behaviour is identical

    .. automethod:: connect
    """
    def __init__(self, namespace=UUID, **kw):
        Handler.__init__(self, namespace=namespace)
        _Rabbit.__init__(self, **kw)

    def connect(self, **kw):
        """
        :synopsis: connect the handler to the RabbitMQ server.

        :param exchange: highly recommended, defaults to "ordf"
        :param queue: When specified forms the basis for the queue
            name. If the value were *"test"* then by default, two
            queues with names *test_graph* and *test_changesets* would
            be created and bound to the *ordf.graph* and *ordf.changesets*
            exchanges respectively.
        """
        self.__shutdown__ = False
        kwa = kw.copy()
        kwa.setdefault("exchange", "ordf")
        kwa.setdefault("exchange_type", "fanout")
        kwa.setdefault("queue", "ordf_test")

        def _loop(**kw):
            self.log = getLogger(self.__class__.__name__ + "/%(exchange)s/%(queue)s" % kw)
            self.log.info("consumer starting - exchange: %(exchange)s queue: %(queue)s" % kw)

            consumer = Consumer(connection=self.connection, **kw)

            def _recv(data, message):
                dummy = Graph("IOMemory")
                store = dummy.store
                try:
                    for ident, n3 in data:
                        graph = Graph(identifier=URIRef(ident), store=store)
                        self.log.info("recv %s" % (graph.identifier,))
                        graph.parse(StringIO(n3.encode("utf-8")))
                    self.put(store)
                except:
                    self.log.error(format_exc())
                        
            consumer.register_callback(_recv)

            while True:
                try:
                    msg = consumer.fetch(auto_ack=True, enable_callbacks=True)
                    if msg is None: ## queue empty
                        sleep(1)
                except Exception, e:
                    self.log.error("%s" % format_exc())
                finally:
                    if self.__shutdown__:
                        break

            self.log.info("consumer finishing")

        t = Thread(target=_loop, kwargs=kwa)
        t.start()

    def close(self):
        self.__shutdown__ = True

