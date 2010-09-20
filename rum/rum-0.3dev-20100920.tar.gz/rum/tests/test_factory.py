from unittest import TestCase
from peak.rules import rules_for, AmbiguousMethods
from rum.basefactory import BaseFactory
from rum.genericfunctions import generic

# We need to redeclare get here because we're clearing the rules on every
# setUp and we don't want to mess other tests
class DummyFactory(BaseFactory):
    @generic
    def get(self, resource, foo=None, bar=None, args=None):
        pass

class Resource(object):
    pass

class Product(object):
    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

class TestBaseFactory(TestCase):
    def setUp(self):
        rules_for(DummyFactory.get).clear()

    def makeOne(self):
        return DummyFactory()

class TestRegister(TestBaseFactory):
    def test_resource_as_class(self):
        DummyFactory.register(Product, Resource)
        prod = self.makeOne()(Resource)
        self.failUnless(isinstance(prod, Product), prod)
        self.failUnlessEqual(prod.a, None, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)
           
    def test_product_as_instance(self):
        DummyFactory.register(Product(), Resource)
        prod = self.makeOne()(Resource)
        self.failUnless(isinstance(prod, Product), prod)
        self.failUnlessEqual(prod.a, None, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)

    def test_values_as_conds(self):
        DummyFactory.register(Product, Resource)
        DummyFactory.register(Product(a=1), Resource, foo=2)
        prod = self.makeOne()(Resource, foo=2)
        self.failUnless(isinstance(prod, Product), prod)
        self.failUnlessEqual(prod.a, 1, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)

    def test_classes_as_conds(self):
        class AClass(object): pass
        DummyFactory.register(Product, Resource)
        DummyFactory.register(Product(a=1), Resource, foo=AClass)

        prod = self.makeOne()(Resource, foo=AClass)
        self.failUnless(isinstance(prod, Product), prod)
        self.failUnlessEqual(prod.a, 1, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)

    def test_pred(self):
        DummyFactory.register(Product, Resource, "foo>1")
        prod = self.makeOne()(Resource, foo=2)
        self.failUnless(isinstance(prod, Product), prod)
        self.failUnlessEqual(prod.a, None, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)

    def test_ambiguous(self):
        DummyFactory.register(Product(a=1), Resource)
        DummyFactory.register(Product(a=2), Resource)
        factory = self.makeOne()
        self.failUnlessRaises(AmbiguousMethods, factory, Resource)

    def test_prio(self):
        DummyFactory.register(Product(a=1), Resource)
        DummyFactory.register(Product(a=2), Resource, _prio=1)
        prod = self.makeOne()(Resource)
        self.failUnlessEqual(prod.a, 2, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)

    def test_ambiguous(self):
        DummyFactory.register(Product(a=1), Resource)
        DummyFactory.register(Product(a=2), Resource)
        factory = self.makeOne()

class TestFactory(TestBaseFactory):
    def test_defaults(self):
        """Keywords passed to the factory are used as dflts. for prods."""
        DummyFactory.register(Product, Resource)
        prod = self.makeOne()(Resource, a=4)
        self.failUnless(isinstance(prod, Product), prod)
        self.failUnlessEqual(prod.a, 4, prod.a)
        self.failUnlessEqual(prod.b, None, prod.b)
