try:
    import json
except ImportError:
    import simplejson as json

from twisted.internet import defer
from twisted.trial import unittest

from quebert import amqp

class FakeAMQPChannel(object):
    exchange = None
    routing_key = None
    content = None
    delivery_tag = None
    recover = None

    def __init__(self, l=None, failAck=False):
        self.failAck = failAck
        self.l = l
        if l is None:
            self.l = []

    def basic_publish(self, exchange, routing_key, content):
        self.exchange = exchange
        self.routing_key = routing_key
        self.content = content

    def basic_ack(self, delivery_tag):
        if self.failAck:
            raise Exception("Need to fail the ack")
        self.delivery_tag = delivery_tag

    def basic_recover(self, requeue):
        self.recover = requeue

    def basic_qos(self, prefetch_count):
        self.l.append(prefetch_count)

class FakeQueue(object):
    def __init__(self, msg):
        self.msg = msg
        self.i = 0

    def get(self):
        if self.i < 3:
            self.i += 1
            return defer.succeed(self.msg)
        return defer.fail(Exception("disconnects"))

class TestAMQPWrapper(unittest.TestCase):
    """
    Note that C{quebert.amqp} is actually for 90% code that will
    either work or not work on startup.

    It's also extremely complex to test without tons of mock-up
    objects and/or with rabbitmq active and alive.

    However since, as written above, most of that code immediately
    signals it's functioning state by actually connecting I think I
    can close an eye on its tests.
    """

    def test_requeue(self):
        """
        C{amqp.TxAMQPClient.requeue} requeues tasks when they have
        some new content.
        """
        c = FakeAMQPChannel()

        class Original(object):
            delivery_tag = "something"
            children = "foobar"
            properties = "hello"
            body = "original content"

        o = Original()
        o.content = Original()

        class FakeMediator(object):
            def encode(self, message):
                return json.dumps(message)

            def decodeMessage(self, message):
                return json.loads(message)

        w = amqp.Watcher("A", None, c, "flow", "a.b")
        w.requeue("Should be an exc", FakeMediator(), "Something", o)

        self.assertEquals(c.exchange, "flow")
        self.assertEquals(c.routing_key, "a.b")
        self.assertEquals(c.content.body, '"Something"')
        self.assertEquals(c.content.children, "foobar")
        self.assertEquals(c.content.properties, "hello")


    def test_wrappedCallback(self):
        """
        C{amqp.Watcher.wrappedCallback} wraps a given callback in
        a"deferred cycle" to ease going back to waiting for new
        messages and to streamline the "transaction" of task processing.
        """
        q = None
        c = FakeAMQPChannel()

        class Original(object):
            delivery_tag = "something"
            children = "foobar"
            properties = "hello"
            body = json.dumps(dict(params=u"original message"))

        o = Original()
        o.content = Original()

        q = FakeQueue(o)
        class FakeMediator(object):
            def __init__(self, l, rais=False):
                self.l = l
                self.rais = rais
            def decodeMessage(self, message):
                return json.loads(message)
            def taskReceived(self, task):
                self.l.append(task)
                if self.rais:
                    raise Exception(task)

        l = []
        w = amqp.Watcher("a", q, c, "flow", "a.b")
        w.wrappedCallback(FakeMediator(l), o)

        # The callback was called and the message acked
        self.assertEquals(c.delivery_tag, o.delivery_tag)
        self.assertEquals(l, [json.loads(o.body)])

        # No requeue called because call returns None.
        self.assertEquals(c.exchange, None)
        self.assertEquals(c.routing_key, None)
        self.assertEquals(c.content, None)
        self.assertEquals(c.recover, None)

        c = FakeAMQPChannel()
        l = []
        w = amqp.Watcher("a", q, c, "flow", "a.b")
        w.wrappedCallback(FakeMediator(l, True), o)

        # The callback was called and the message acked
        self.assertEquals(c.delivery_tag, o.delivery_tag)
        self.assertEquals(l, [json.loads(o.body)])

        # This time there's a requeue because we returned something
        self.assertEquals(c.exchange, "flow")
        self.assertEquals(c.routing_key, "a.b")
        self.assertEquals(c.content.body, '{"params": "original message"}')
        self.assertEquals(c.recover, None)
        self.flushLoggedErrors()

        c = FakeAMQPChannel(failAck=True)
        l = []
        w = amqp.Watcher("a", q, c, "flow", "a.b")
        w.wrappedCallback(FakeMediator(l), o)
        self.assertEquals(c.recover, True)
        self.flushLoggedErrors()

    def test_loop(self):
        """
        C{amqp.Watcher.loop} loops using deferreds and calls itself
        over and over from the deferred.
        """

        c = FakeAMQPChannel()

        class Original(object):
            delivery_tag = "something"
            children = "foobar"
            properties = "hello"
            body = json.dumps(dict(body="original message"))

        o = Original()
        o.content = Original()

        q = FakeQueue(o)

        w = amqp.Watcher("a", q, c, "flow", "a.b")

        l = []
        e = []
        def exc(r):
            e.append(r)

        class FakeMediator(object):
            def decodeMessage(self, message):
                return json.loads(message)
            def taskReceived(self, task):
                l.append(task)


        # Since q has a count on self.i, this should only
        # be 3 loops.
        w.loop(FakeMediator(), onDisconnect=exc)
        self.assertEquals(len(l), 3)
        self.assertEquals(len(e), 1)

    def test_prefetchCount(self):
        """
        When C{amqp.Watcher.currentEvents} changes basic_qos is called
        to change the prefetch window.
        """

        l = []
        c = FakeAMQPChannel(l)

        w = amqp.Watcher("foo", None, c, "flow", "a.b")

        w._currentEvents = 5

        w.increaseEvents(None)
        w.increaseEvents(0)
        w.decreaseEvents(None)
        w.decreaseEvents(0)
        self.assertEquals(l, [])

        w.increaseEvents(5)
        self.assertEquals(l, [6])
        w.increaseEvents(5)
        self.assertEquals(l, [6, 7])
        w.increaseEvents(5)
        self.assertEquals(l, [6, 7, 8])
        w.decreaseEvents(5)
        self.assertEquals(l, [6, 7, 8, 7])
        w.decreaseEvents(5)
        self.assertEquals(l, [6, 7, 8, 7, 6])
        w.decreaseEvents(5)
        self.assertEquals(l, [6, 7, 8, 7, 6, 5])
        w.decreaseEvents(5)
        self.assertEquals(l, [6, 7, 8, 7, 6, 5])
        w.decreaseEvents(5)
        self.assertEquals(l, [6, 7, 8, 7, 6, 5])

    def test_startTimeout(self):
        """
        C{amqp.Watcher.startTimeout} starts a timeout counter and
        returns a function that cancels it.
        """

        calls = []

        class FakeDelayedCall(object):
            def __init__(self, isActive):
                self.isActive = isActive
            def active(self):
                return self.isActive
            def cancel(self):
                calls.append("cancel")
        class FakeReactor(object):
            def __init__(self, isActive):
                self.isActive = isActive
            def callLater(self, sec, fun, *args):
                return FakeDelayedCall(self.isActive)

        l = []
        c = FakeAMQPChannel(l)
        w = amqp.Watcher("foo", None, c, "flow", "a.b", FakeReactor(True))
        cancel = w.startTimeout(10, 5)
        cancel(None)
        self.assertEquals(calls, ["cancel"])

        l = []
        c = FakeAMQPChannel(l)
        w = amqp.Watcher("foo", None, c, "flow", "a.b", FakeReactor(False))
        w._currentEvents = 5
        cancel = w.startTimeout(10, 3)
        cancel(None)
        self.assertEquals(l, [4])

    ## def test_delayMediator(self):
    ##     """
    ##     C{m.DelayOnErrorMediator} uses exponential backoff to reschedule
    ##     failed tasks.
    ##     """

    ##     t = m.DelayOnErrorMediator()
    ##     self.assertEquals(t.excepthook, t.backoff)
    ##     self.assertEquals(t.constant, 1.5)
    ##     self.assertEquals(t.maxDelay, 120)

    ##     t = m.DelayOnErrorMediator(constant=10, maxDelay=50)
    ##     self.assertEquals(t.excepthook, t.backoff)
    ##     self.assertEquals(t.constant, 10)
    ##     self.assertEquals(t.maxDelay, 50)

    ##     class FakeReactor(object):
    ##         delay = None
    ##         def callLater(self, delay, func, *args):
    ##             self.delay = delay
    ##             self.func = func
    ##             self.args = args
    ##         def call(self):
    ##             self.func(*self.args)

    ##     r = FakeReactor()
    ##     t = m.DelayOnErrorMediator(constant=10, maxDelay=50, reactor=r)

    ##     ARG = dict(foo="bar", boz="fob")
    ##     task = dict(
    ##         url=u"/bar",
    ##         params=ARG
    ##     )

    ##     t.backoff("hello", task)

    ##     self.assertEquals(task['failures'], 1)
    ##     self.assertEquals(task['traceback'], "hello")
    ##     self.assertEquals(r.delay, 10)

    ##     task = dict(
    ##         url=u"/bar",
    ##         params=ARG,
    ##         failures=20
    ##     )


    ##     t.backoff("hello", task)

    ##     self.assertEquals(task['failures'], 21)
    ##     self.assertEquals(task['traceback'], "hello")
    ##     self.assertEquals(r.delay, 50)
    ##     # Check that I'm calling a callback and not an errback
    ##     return r.call()
