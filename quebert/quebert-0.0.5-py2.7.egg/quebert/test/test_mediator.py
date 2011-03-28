try:
    import json
except:
    import simplejson as json

from datetime import timedelta

from twisted.internet import defer
from twisted.trial import unittest

from quebert import mediator as m, common as qc

class TestMediator(unittest.TestCase):
    def test_hooks(self):
        """
        C{m.Mediator.addPrehook} returns hooks in the same order they are added.
        C{m.Mediator.addPosthook} returns hooks in the reverse order they are added.
        C{m.Mediator._executeHooks} calls the hooks in the order they are passed.
        """
        t = m.Mediator()
        t.addPrehook(1)
        t.addPrehook(2)
        t.addPrehook(3)
        self.assertEquals(t.prehooks, [1,2,3])

        t.addPosthook(1)
        t.addPosthook(2)
        t.addPosthook(3)
        self.assertEquals(t.posthooks, [3,2,1])

        v = [False]
        def fun(exc, t):
            v[0] = True
        t.excepthook = fun
        t.excepthook(1, 2)
        self.assert_(v[0])

        def f(t):
            l.append(t)
            return "bla"

        def f1(t):
            l.append(t+1)
            return "something"

        t = m.Mediator()
        def cb(v):
            self.assertEquals(v, None)
            self.assertEquals(l, [1,2,2,1])
        l = []
        t._executeHooks([f, f1, f1, f], 1).addCallback(cb)

        def cb2(v):
            self.assertEquals(v, None)
            self.assertEquals(l, [2])
        l = []
        t._executeHooks([f1], 1).addCallback(cb2)

    def test_urlparsing(self):
        """
        C{m.Mediator} constructor parses the passed url,
        then normalizeUrl creates a full URL from those values
        """

        t = m.Mediator()
        self.assertEquals(t.defaultscheme, "http")
        self.assertEquals(t.defaultnetloc, "localhost:8000")

        t = m.Mediator(defaulturl="https://localhost/")
        self.assertEquals(t.defaultscheme, "https")
        self.assertEquals(t.defaultnetloc, "localhost")

        t = m.Mediator(defaulturl="")
        self.assertEquals(t.defaultscheme, "http")
        self.assertEquals(t.defaultnetloc, "localhost")

        t = m.Mediator()
        self.assertEquals(t.normalizeUrl("/foo"), "http://localhost:8000/foo")
        self.assertEquals(t.normalizeUrl("http://localhost/foo"), "http://localhost/foo")

    def test_makeRequest(self):
        """
        C{m.Mediator.makeRequest} makes a request and decodes
        the response as JSON by default.
        """

        ARG = dict(foo="bar", boz="fob", timeout=10)
        RESULT = dict(res="ok")
        def getPage(url, method, timeout, postdata, headers):
            self.assertEquals(url, "http://localhost:8000/foo")
            self.assertEquals(method, "POST")
            self.assertEquals(timeout, 10)
            self.assertEquals(postdata, json.dumps(ARG))
            return defer.succeed(json.dumps(RESULT))

        t = m.Mediator(getPage=getPage)
        t.makeRequest("http://localhost:8000/foo", ARG
                      ).addCallback(self.assertEquals, RESULT)

        task = dict(
            url=u"/bar",
            params=json.dumps("hello")
        )

        def getPage(url, method, timeout, postdata, headers):
            self.assertEquals(url, "http://localhost:8000/bar")
            self.assertEquals(method, "POST")
            self.assertEquals(timeout, 0)
            self.assertEquals(postdata, json.dumps(task))
            return defer.succeed(json.dumps(RESULT))

        t = m.Mediator(getPage=getPage)
        t.processTask(task).addCallback(self.assertEquals, RESULT)

        def getPage(*args):
            raise Exception("I shouldn't be raised")

        # if this actually executes the getPage will raise the exception
        t = m.Mediator(getPage=getPage)
        task['filter'] = True
        return t.processTask(task)

    def test_taskReceived(self):
        """
        C{m.Mediator.taskReceived} is the entrance point for all the
        functionality in the mediator.
        """

        ARG = dict(foo="bar", boz="fob")
        RESULT = dict(res="ok")

        task = dict(
            url=u"/bar",
            params=json.dumps(ARG)
        )

        l = []
        def hook(v, r=None):
            self.assertEquals(v, task)
            if r is not None:
                self.assertEquals(r, RESULT)
            l.append(1)

        def getPage(url, method, timeout, postdata, headers):
            self.assertEquals(url, "http://localhost:8000/bar")
            self.assertEquals(method, "POST")
            self.assertEquals(timeout, 0)
            self.assertEquals(postdata, json.dumps(task))
            return defer.succeed(json.dumps(RESULT))

        t = m.Mediator(getPage=getPage)
        t.addPrehook(hook)
        t.addPrehook(hook)
        t.addPosthook(hook)
        t.addPosthook(hook)
        t.taskReceived(dict(task)
              ).addCallback(lambda _: self.assertEquals(l, [1,1,1,1]))

        l = []
        t = m.Mediator(getPage=getPage)
        t.taskReceived(dict(task)
              ).addCallback(lambda _: self.assertEquals(l, []))

        t = m.Mediator(getPage=getPage)
        self.assertEquals(ARG, t.decode(json.dumps(ARG)))

        def getPage(*args, **kwargs):
            raise Exception("fooobar")

        t = m.Mediator(getPage=getPage)

        task['ttl'] = 1
        task['timestamp'] = qc.serialize_date(qc.now()+timedelta(seconds=10))
        self.assertFailure(t.taskReceived(dict(task)), Exception)

        l = []
        t = m.Mediator(getPage=getPage)

        task['ttl'] = 1
        task['timestamp'] = qc.serialize_date(qc.now()-timedelta(seconds=2))
        t.taskReceived(dict(task))

        t.taskReceived(None)
