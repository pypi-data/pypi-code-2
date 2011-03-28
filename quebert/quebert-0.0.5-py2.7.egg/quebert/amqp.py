try:
    import json
except ImportError:
    import simplejson as json

import itertools

from twisted.python import filepath, log
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientCreator

from txamqp.content import Content
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp import spec

fp = filepath.FilePath(__file__).parent().child('amqp0-8.xml')
amqp08 = spec.load(fp.path)

gen_id = itertools.count(1).next # start from 1.

class Watcher(object):
    def __init__(self, queueName, queue, channel, exchange,
                 routingKey, reactor=reactor, decode=json.loads,
                 encode=json.dumps):
        self.queueName = queueName
        self.queue = queue
        self.channel = channel
        self.exchange = exchange
        self.routingKey = routingKey
        self.reactor = reactor

        self.encode = encode
        self.decode = decode

        self._currentEvents = None
        self.maxEvents = None

    def decodeMessage(self, message):
        try:
            task = self.decode(message)
        except Exception, e:
            log.msg("Error decoding %s..." % (message,))
            log.err(e)
            return
        return task

    def pcurrentEvents():
        def fget(self):
            return self._currentEvents
        def fset(self, value):
            if value is not None and value != self._currentEvents:
                self._currentEvents = value
                log.msg("Prefetch window on %s set to %s" % (self.queueName, value))
                self.channel.basic_qos(prefetch_count=value)
        return locals()
    currentEvents = property(**pcurrentEvents())

    def loop(self, mediator, timeout=0, maxEvents=None, onDisconnect=None):
        """
        Loop through the messages that are coming and diversify in 2 branches:
         * when queue.get() errbacks it means that there was a disconnect or
            a bad problem, don't restart the loop
         * In case the loop is successful instead we can keep on looping.

        This is not a public API so there's no point explaining every argument
        which anyway comes directly from C{TxAMQPClient.watch} call.
        """
        def successful(msg):
            # Note that here there's a performance hack... instead of
            # doing things serially we do multiple messages at the same
            # time, if something goes wrong we call the basic_recover
            # of course since it's not the only thing going on at the
            # same time, there recover will work for every message not
            # acked, this means that we might end up with some messages
            # notified more than once.
            # if you want to do stuff serially use addCallback to call
            # the loop.
            cancelFunction = self.startTimeout(timeout, maxEvents)
            self.wrappedCallback(mediator, msg).addCallback(cancelFunction)
            return self.loop(mediator, timeout, maxEvents, onDisconnect)

        if onDisconnect is None:
            onDisconnect = lambda reason: log.err(reason)

        if self.currentEvents is None:
            self.currentEvents = maxEvents
            self.maxEvents = maxEvents

        self.queue.get().addCallbacks(successful, onDisconnect)

    def requeue(self, reason, mediator, message, original):
        """
        I run before the ack is sent so that I'm virtually inside a
        transaction with rabbitmq. I can requeue tasks that had issues
        and then the system proceeds to acknowlede the one that just
        failed, this way I can enrich the task content without losing
        it, worst that could happen is a task duplicate.

        I call the exceptionHandler and it should return a string version
        of the task that I should republish before the original one is
        acked.
        """
        def _cb(newtask):
            try:
                newcontent = self.encode(newtask)
            except Exception, e:
                log.msg("Error while trying to encode %s" % (message,))
                log.err(e)
                # we can't discard anything here, otherwise we would go
                # in an infinite loop immediately, we know the old message
                # worked fine so we simply use it, if there was a delay
                # exception that has already been taken care of because
                # we come after the exceptionHandler.
                log.msg("Reusing old")
                newcontent = original.content.body.strip()

            original_content = original.content
            content = Content(newcontent,
                              original_content.children,
                              original_content.properties)

            return self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routingKey,
                content=content
            )
        d = defer.maybeDeferred(self.exceptionHandler, reason, message)
        return d.addCallback(_cb)

    def exceptionHandler(self, reason, message):
        """
        Handles the exception raised while executing a task.
        I receive the external message format.
        """
        log.msg("Handling with error by rescheduling immediately")
        log.err(reason)
        return message

    def wrappedCallback(self, mediator, msg):
        """
        I wrap a user callback to make it easier to use me.

        Depending on how I work I can do the following things:

        * Correctly handle the message and acknowledge it
        * If there's an error before a successful acknowledgement
           I ask the server to redeliver my messages
        * I check for new messages again.
        """
        def _eb(reason):
            log.err(reason)
            return self.channel.basic_recover(requeue=True)

        message = self.decodeMessage(msg.content.body.strip())
        # We expect message to be a mutable object.
        return defer.maybeDeferred(mediator.taskReceived, message
            ).addErrback(self.requeue, mediator, message, msg
            ).addCallback(lambda _: self.channel.basic_ack(msg.delivery_tag)
            ).addErrback(_eb)

    def startTimeout(self, timeout, maxEvents):
        if timeout and maxEvents:
            timeoutID = self.reactor.callLater(timeout, self.increaseEvents, maxEvents)
            def cancel(_):
                if timeoutID.active():
                    timeoutID.cancel() # no need to use the timeout
                    return
                return self.decreaseEvents(maxEvents)
            return cancel

        return lambda _: None

    def increaseEvents(self, maxEvents=None):
        if maxEvents is None:
            maxEvents = self.maxEvents
        if maxEvents is not None and maxEvents > 0:
            self.currentEvents = self.currentEvents + 1

    def decreaseEvents(self, maxEvents=None):
        if maxEvents is None:
            maxEvents = self.maxEvents
        if maxEvents is not None and maxEvents > 0:
            self.currentEvents = max(self.currentEvents-1, maxEvents)


class TxAMQPClient(object):
    """
    Twisted AMQP Client class, it's an abstraction to ease the
    monitoring of an AMQP queue.

    @ivar host: The host to which connect
    @ivar username: Username that should be used for connection
    @ivar password: Password for the connection
    """
    watcherFactory = Watcher

    def __init__(self, host, username, password,
                 reactor=reactor, watcherFactory=None):
        self.host = host
        self.username = username
        self.password = password
        self.reactor = reactor
        if watcherFactory:
            self.watcherFactory = watcherFactory

    def connect(self):
        """
        Connect to the AMQP server and store a client instance in the
        instance to make it more easily accessible from the outside.
        """
        from twisted.internet import reactor
        delegate = TwistedDelegate()
        return ClientCreator(reactor, AMQClient, delegate, "/", amqp08
                                ).connectTCP(self.host, 5672)

    def login(self, client):
        """
        Login into the service and create a new channel with unique id.
        """
        def _onStart(_):
            return client.channel(gen_id())
        auth = {"LOGIN": self.username, "PASSWORD": self.password}
        return client.start(auth).addCallback(_onStart)

    @defer.inlineCallbacks
    def setup_connection(self, exchange, exchangeType="topic"):
        """
        Setup the connection and return a channel to the broker with
        the given interface setup.

        @param exchange: The exchange name
        @type exchange: C{str}
        """
        log.msg("Signing in...")
        client = yield self.connect()

        channel = yield self.login(client)

        log.msg("Opening channel...")
        yield channel.channel_open()

        log.msg("Creating the exchange %s..." % (exchange,))
        yield channel.exchange_declare(exchange=exchange, type=exchangeType,
                                       durable=True, auto_delete=False)

        defer.returnValue((client, channel))

    @defer.inlineCallbacks
    def watch(self, exchange, queue, routingKey, exchangeType="topic",
              decode=json.loads, encode=json.dumps):
        """
        Watch a given exchange-queue-routingKey combination and when
        a message is delivered call callback.

        @param exchange: The exchange name
        @type exchange: C{str}

        @param queue: The queue name
        @type queue: C{str}

        @param routingKey: The routing key to bind the exchange and the queue
        @type routingKey: C{str}, # is a catchall

        @param exchangeType: The type of exchange we want to create.
        @type exchangeType: C{str}, can be many, see AMQP documentation.
        """
        client, channel = yield self.setup_connection(exchange, exchangeType)

        log.msg("Creating the queue %s..." % (queue,))
        yield channel.queue_declare(queue=queue, durable=True, auto_delete=False)

        log.msg("Binding the queue to routing key %s..." % (routingKey,))
        yield channel.queue_bind(queue=queue, exchange=exchange,
                                 routing_key=routingKey)

        reply = yield channel.basic_consume(queue=queue)
        q = yield client.queue(reply.consumer_tag)

        log.msg("Waiting for messages...")
        w = self.watcherFactory(queue, q, channel, exchange, routingKey,
                                self.reactor, decode, encode)
        defer.returnValue(w)

