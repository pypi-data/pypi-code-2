import unittest
from repoze.depinj import clear

class TestDependencyInjector(unittest.TestCase):
    def _makeOne(self):
        from repoze.depinj import DependencyInjector
        return DependencyInjector()

    def test_ctor(self):
        injector = self._makeOne()
        self.assertEqual(injector.factories, {})
        self.assertEqual(injector.lookups, {})
        self.assertEqual(injector.factory_results, {})

    def test_inject_factory(self):
        injector = self._makeOne()
        thunk = injector.inject_factory(DummyFactory, Dummy)
        injector.factory_results[(thunk, Dummy)] = 'abc'
        self.assertEqual(thunk(), 'abc')

    def test_inject(self):
        injector = self._makeOne()
        injector.inject(Dummy, Dummy2)
        self.assertEqual(injector.lookups[Dummy2], [Dummy])

    def test_construct_injected(self):
        injector = self._makeOne()
        injector.factories[Dummy] = [(None, DummyFactory)]
        result = injector.construct(Dummy, 'one', 'two', a=1, b=2)
        self.assertEqual(result.arg, ('one', 'two'))
        self.assertEqual(result.kw, {'a':1, 'b':2})

    def test_construct_not_injected(self):
        injector = self._makeOne()
        result = injector.construct(DummyFactory, 'one', 'two', a=1, b=2)
        self.assertEqual(result.arg, ('one', 'two'))
        self.assertEqual(result.kw, {'a':1, 'b':2})

    def test_lookup_injected(self):
        injector = self._makeOne()
        injector.lookups[Dummy] = [Dummy2]
        result = injector.lookup(Dummy)
        self.assertEqual(result, Dummy2)

    def test_lookup_notinjected(self):
        injector = self._makeOne()
        result = injector.lookup(Dummy)
        self.assertEqual(result, Dummy)

class Test_lookup(unittest.TestCase):
    def setUp(self):
        clear()

    def tearDown(self):
        clear()

    def test_it_injected(self):
        from repoze.depinj import lookup
        from repoze.depinj import injector
        injector.inject('123', 'whatever')
        self.assertEqual(lookup('whatever'), '123')

    def test_it_not_injected(self):
        from repoze.depinj import lookup
        self.assertEqual(lookup('whatever'), 'whatever')

    def test_it_with_a_dict_injected(self):
        from repoze.depinj import lookup
        from repoze.depinj import injector
        dummy = {'foo': 'bar'}
        injector.inject('foo', dummy)
        dummy['foo'] = 'baz'  # prove lookup is done on object itself
        self.assertEqual(lookup(dummy), 'foo')

    def test_it_not_injected(self):
        from repoze.depinj import lookup
        dummy = {'foo': 'bar'}
        self.assertEqual(lookup(dummy), dummy)

class Test_construct(unittest.TestCase):
    def setUp(self):
        clear()

    def tearDown(self):
        clear()

    def test_it_injected(self):
        from repoze.depinj import construct
        from repoze.depinj import injector
        promise = injector.inject_factory(DummyFactory, 'whatever')
        self.assertEqual(construct('whatever', 'a', b=1).__class__,DummyFactory)
        fixture = promise()
        self.assertEqual(fixture.arg, ('a',))
        self.assertEqual(fixture.kw, {'b':1})

    def test_it_not_injected(self):
        from repoze.depinj import construct
        self.assertEqual(construct(DummyFactory).__class__, DummyFactory)

class Test_inject_factory(unittest.TestCase):
    def setUp(self):
        clear()

    def tearDown(self):
        clear()

    def test_it(self):
        from repoze.depinj import inject_factory
        from repoze.depinj import injector
        thunk = inject_factory(Dummy, DummyFactory)
        injector.factory_results[(thunk, DummyFactory)] = 'result'
        self.assertEqual(thunk(), 'result')

class Test_inject(unittest.TestCase):
    def setUp(self):
        clear()

    def tearDown(self):
        clear()

    def test_it(self):
        from repoze.depinj import inject
        from repoze.depinj import injector
        inject(Dummy, DummyFactory)
        self.assertEqual(injector.lookups[DummyFactory], [Dummy])

class TestFactoryOrdering(unittest.TestCase):
    def setUp(self):
        clear()

    def tearDown(self):
        clear()

    def test_it(self):
        from repoze.depinj import inject_factory
        from repoze.depinj import construct
        def factory1():
            return 'factory1'
        def factory2():
            return 'factory2'
        thunk1 = inject_factory(factory1, Dummy)
        thunk2 = inject_factory(factory2, Dummy)
        construct(Dummy)
        construct(Dummy)
        self.assertEqual(thunk2(), 'factory2')
        self.assertEqual(thunk1(), 'factory1')
        self.assertEqual(construct(Dummy).__class__, Dummy)

class TestLookupOrdering(unittest.TestCase):
    def setUp(self):
        clear()

    def tearDown(self):
        clear()

    def test_it(self):
        from repoze.depinj import inject
        from repoze.depinj import lookup
        inject('ob1', Dummy)
        inject('ob2', Dummy)
        self.assertEqual(lookup(Dummy), 'ob1')
        self.assertEqual(lookup(Dummy), 'ob2')
        self.assertEqual(lookup(Dummy), Dummy)


class DummyInjector(object):
    def __init__(self, constructed=None, looked_up=None, result=None):
        self.constructed = constructed
        self.looked_up = looked_up
        self.result = result

    def lookup(self, real):
        return self.looked_up

    def construct(self, real, *arg, **kw):
        self.construct_args = arg, kw
        return self.constructed

class Dummy(object):
    pass

class Dummy2(object):
    pass

class DummyFactory(object):
    def __init__(self, *arg, **kw):
        self.arg = arg
        self.kw = kw

