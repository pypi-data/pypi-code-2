# -*- test-case-name: buildbot.broken_test.test_util -*-

from twisted.trial import unittest

from buildbot import util


class ComparableMixin(unittest.TestCase):
    class Foo(util.ComparableMixin):
        compare_attrs = ["a", "b"]
        def __init__(self, a, b, c):
            self.a, self.b, self.c = a,b,c

    class Bar(Foo, util.ComparableMixin):
        compare_attrs = ["b", "c"]

    def setUp(self):
        self.f123 = self.Foo(1, 2, 3)
        self.f124 = self.Foo(1, 2, 4)
        self.f134 = self.Foo(1, 3, 4)
        self.b123 = self.Bar(1, 2, 3)
        self.b223 = self.Bar(2, 2, 3)
        self.b213 = self.Bar(2, 1, 3)

    def test_equality_identity(self):
        self.assertEqual(self.f123, self.f123)

    def test_equality_same(self):
        another_f123 = self.Foo(1, 2, 3)
        self.assertEqual(self.f123, another_f123)

    def test_equality_unimportantDifferences(self):
        self.assertEqual(self.f123, self.f124)

    def test_equality_unimportantDifferences_subclass(self):
        # verify that the parent class's compare_attrs doesn't
        # affect the subclass
        self.assertEqual(self.b123, self.b223)

    def test_inequality_importantDifferences(self):
        self.assertNotEqual(self.f123, self.f134)

    def test_inequality_importantDifferences_subclass(self):
        self.assertNotEqual(self.b123, self.b213)

    def test_inequality_differentClasses(self):
        self.assertNotEqual(self.f123, self.b123)

    def test_lt_importantDifferences(self):
        assert self.f123 < self.f134

    def test_lt_differentClasses(self):
        assert self.b123 < self.f123
