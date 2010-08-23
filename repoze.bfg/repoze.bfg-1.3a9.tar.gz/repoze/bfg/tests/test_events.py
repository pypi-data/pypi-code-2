import unittest

class NewRequestEventTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.events import NewRequest
        return NewRequest

    def _makeOne(self, request):
        return self._getTargetClass()(request)

    def test_class_implements(self):
        from repoze.bfg.interfaces import INewRequest
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(INewRequest, klass)
        
    def test_instance_implements(self):
        from repoze.bfg.interfaces import INewRequest
        from zope.interface.verify import verifyObject
        request = DummyRequest()
        inst = self._makeOne(request)
        verifyObject(INewRequest, inst)

    def test_ctor(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        self.assertEqual(inst.request, request)

class NewResponseEventTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.events import NewResponse
        return NewResponse

    def _makeOne(self, response):
        return self._getTargetClass()(response)

    def test_class_implements(self):
        from repoze.bfg.interfaces import INewResponse
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(INewResponse, klass)
        
    def test_instance_implements(self):
        from repoze.bfg.interfaces import INewResponse
        from zope.interface.verify import verifyObject
        response = DummyResponse()
        inst = self._makeOne(response)
        verifyObject(INewResponse, inst)

    def test_ctor(self):
        response = DummyResponse()
        inst = self._makeOne(response)
        self.assertEqual(inst.response, response)

class WSGIAppEventTests(unittest.TestCase):
    def test_object_implements(self):
        from repoze.bfg.events import WSGIApplicationCreatedEvent
        event = WSGIApplicationCreatedEvent(object())
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        from zope.interface.verify import verifyObject
        verifyObject(IWSGIApplicationCreatedEvent, event)

    def test_class_implements(self):
        from repoze.bfg.events import WSGIApplicationCreatedEvent
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        from zope.interface.verify import verifyClass
        verifyClass(IWSGIApplicationCreatedEvent, WSGIApplicationCreatedEvent)

class AfterTraversalEventTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.events import AfterTraversal
        return AfterTraversal

    def _makeOne(self, request):
        return self._getTargetClass()(request)

    def test_class_implements(self):
        from repoze.bfg.interfaces import IAfterTraversal
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(IAfterTraversal, klass)
        
    def test_instance_implements(self):
        from repoze.bfg.interfaces import IAfterTraversal
        from zope.interface.verify import verifyObject
        request = DummyRequest()
        inst = self._makeOne(request)
        verifyObject(IAfterTraversal, inst)

    def test_ctor(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        self.assertEqual(inst.request, request)

class TestSubscriber(unittest.TestCase):
    def setUp(self):
        registry = DummyRegistry()
        from repoze.bfg.configuration import Configurator
        self.config = Configurator(registry)
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _makeOne(self, *ifaces):
        from repoze.bfg.events import subscriber
        return subscriber(*ifaces)

    def test_register(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne(IFoo, IBar)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.subscribed, [(foo, (IFoo, IBar))])

    def test___call__(self):
        dec = self._makeOne()
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached, [(foo, dec.register, 'bfg')])

class DummyConfigurator(object):
    def __init__(self):
        self.subscribed = []

    def add_subscriber(self, wrapped, ifaces):
        self.subscribed.append((wrapped, ifaces))

class DummyRegistry(object):
    pass
        
class DummyVenusian(object):
    def __init__(self):
        self.attached = []

    def attach(self, wrapped, fn, category=None):
        self.attached.append((wrapped, fn, category))

class Dummy:
    pass
        
class DummyRequest:
    pass

class DummyResponse:
    pass

