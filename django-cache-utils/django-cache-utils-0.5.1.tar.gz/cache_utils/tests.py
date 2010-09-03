#coding: utf-8

from unittest import TestCase

from django.core.cache import cache
from cache_utils.decorators import cached
from cache_utils.utils import sanitize_memcached_key

class ClearMemcachedTest(TestCase):
    def tearDown(self):
        cache._cache.flush_all()

    def setUp(self):
        cache._cache.flush_all()


class InvalidationTest(ClearMemcachedTest):

    def testInvalidation(self):
        cache.set('vasia', 'foo', 60, group='names')
        cache.set('petya', 'bar', 60, group='names')
        cache.set('red', 'good', 60, group='colors')

        self.assertEqual(cache.get('vasia', group='names'), 'foo')
        self.assertEqual(cache.get('petya', group='names'), 'bar')
        self.assertEqual(cache.get('red', group='colors'), 'good')

        cache.invalidate_group('names')
        self.assertEqual(cache.get('petya', group='names'), None)
        self.assertEqual(cache.get('vasia', group='names'), None)
        self.assertEqual(cache.get('red', group='colors'), 'good')

        cache.set('vasia', 'foo', 60, group='names')
        self.assertEqual(cache.get('vasia', group='names'), 'foo')


class UtilsTest(ClearMemcachedTest):

    def testSanitizeKeys(self):
        key = u"12345678901234567890123456789012345678901234567890"
        self.assertTrue(len(key) >= 40)
        key = sanitize_memcached_key(key, 40)
        self.assertTrue(len(key) <= 40)

    def testDecorator(self):
        self._x = 0

        @cached(60, group='test-group')
        def my_func(params=""):
            self._x = self._x + 1
            return u"%d%s" % (self._x, params)

        self.assertEqual(my_func(), "1")
        self.assertEqual(my_func(), "1")

        self.assertEqual(my_func("x"), u"2x")
        self.assertEqual(my_func("x"), u"2x")

        self.assertEqual(my_func(u"Василий"), u"3Василий")
        self.assertEqual(my_func(u"Василий"), u"3Василий")

        self.assertEqual(my_func(u"й"*240), u"4"+u"й"*240)
        self.assertEqual(my_func(u"й"*240), u"4"+u"й"*240)

        self.assertEqual(my_func(u"Ы"*500), u"5"+u"Ы"*500)
        self.assertEqual(my_func(u"Ы"*500), u"5"+u"Ы"*500)
