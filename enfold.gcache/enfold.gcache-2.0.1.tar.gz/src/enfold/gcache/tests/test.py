#
# Copyright: Enfold Systems Ltd
#
#$Id: test.py 4292 2010-08-30 19:57:37Z nikolay $

import unittest, doctest
import sys, os, shutil
import tempfile, time, datetime, new, copy
from cPickle import Pickler, Unpickler
from cStringIO import StringIO

import bsddb
import logging

from enfold.gcache.utils import now
from enfold.gcache.cache import metadata
from enfold.gcache.cache import Cache, CacheStorage
from enfold.gcache.interfaces import Uncachable, ValidationGotNewItem
from enfold.gcache.diskstorage import DiskStorage

logger = logging.getLogger()
hdlr = logging.FileHandler('test.log')
fmt = logging.Formatter(logging.BASIC_FORMAT)
hdlr.setFormatter(fmt)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


class testCacheLimits(unittest.TestCase):
    pass


class Tester:

    _cache_params_ = {}

    def assertInCache(self, *keys):
        for k in keys:
            self.cache.get(k)
            self.cache.getmeta(k)

    def assertNotInCache(self, *keys):
        for k in keys:
            self.assertRaises(KeyError, self.cache.get, k)

    def cache_get(self, key):
        return self.cache.get(key)


class CacheMaker:

    def checkCacheConsistent(self):
        self.cache._check()


class SimpleCacheProvider(object):

    def provide(self, key):
        raise KeyError, key

    def validate(self, key, meta, data):
        raise KeyError, key


class TestObjectCache(Tester):

    skip_test_makers = ["DiskCacheMaker2"]

    def testObjects(self):
        self.cache.set("foo", (None, (1,2)))
        self.assertEqual(self.cache_get("foo"), (1,2))
        if hasattr(self, "reOpen"):
            self.reOpen()
            self.assertEqual(self.cache_get("foo"), (1,2))


class TestCache(Tester):

    def testSimple(self):
        cache = self.cache
        self.assertRaises(KeyError, cache.get, "nothing")
        self.assertEqual(len(cache), 0)
        cache.flush()

    def testCacheConfigure(self):
        self.assertRaises(
            RuntimeError,
            Cache, self.cache.provider, self.cache.data, unknown=None)

        self.assertRaises(
            RuntimeError,
            Cache, self.cache.provider, self.cache.data, max_age=600)

    def testSizes(self):
        cache = self.cache
        self.assertRaises(KeyError, cache.get, "nothing")
        self.assertEqual(len(cache), 0)
        self.cache.set("foo", (None, "aaaaa"))
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache.size, 5)

        meta, data = self.cache.raw_get('foo')

        # recalculate cache size
        cache = Cache(
            self.cache.provider, self.cache.data, logger=logger)

        self.assertEqual(len(cache), 1)
        self.assertEqual(cache.size, 5)

        # cleanup unloadable records on startup
        def get_meta_failed(key):
            raise RuntimeError

        old1 = cache.data.get_meta
        old2 = cache.data.__delitem__
        cache.data.get_meta = get_meta_failed
        cache.data.__delitem__ = get_meta_failed

        cache = Cache(cache.provider, cache.data, logger=logger)

        self.assertEqual(cache.size, 0)

        cache.data.get_meta = old1
        cache.data.__delitem__ = old2
        if not len(self.cache.data):
            self.cache.data['foo'] = (meta,data)

        del self.cache["foo"]
        self.assertEqual(len(self.cache), 0)
        self.assertEqual(self.cache.size, 0)

    def testExpiry(self):
        cache = self.cache
        lnow = now()
        m = metadata(3, lnow, t_stale = lnow + datetime.timedelta(seconds=0.25))
        cache.set("foo", (m, "bar"))
        self.assertEqual(len(cache), 1)
        self.assertEqual(self.cache_get("foo"), "bar")
        time.sleep(0.3)
        self.assertRaises(KeyError, self.cache_get, "foo")
        self.assertEqual(len(cache), 0)

    def testReferenceHeldExpires(self):
        # try to update an item while we hold a reference to the previous data
        # in a case of a diskstorage that returns files, this will prevent
        # it being updated.
        cache = self.cache
        lnow = now()
        m = metadata(3, lnow, t_stale = lnow + datetime.timedelta(seconds=0.25))
        cache.set("foo", (m, "bar"))
        self.assertEqual(len(cache), 1)
        got = self.cache.get("foo")
        time.sleep(0.3)
        self.assertRaises(KeyError, self.cache_get, "foo")
        self.assertEqual(len(cache), 0)
        # now read our file.
        data = got
        if hasattr(got, "read"):
            data = got.read()
        self.assertEqual(data, "bar")

    def testReferenceHeldUpdate(self):
        # try to update an item while we hold a reference to the previous data
        # in a case of a diskstorage that returns files, this will prevent
        # it being updated.
        cache = self.cache
        lnow = now()
        m = metadata(3, lnow)
        cache.set("foo", (m, "bar"))
        self.assertEqual(len(cache), 1)
        got_first = self.cache.get("foo")
        m = metadata(6, lnow)
        cache.set("foo", (m, "second"))
        got_second = self.cache.get("foo")

        data_first = got_first
        if hasattr(data_first, 'read'):
            data_first = data_first.read()
        data_second = got_second
        if hasattr(data_second, 'read'):
            data_second = data_second.read()
        self.assertEqual(data_first, "bar")
        self.assertEqual(data_second, "second")

    def testUpdate(self):
        cache = self.cache
        cache.set("foo", (None, "bar"))
        self.assertEqual(self.cache_get("foo"), "bar")
        self.assertEqual(cache.size, 3)
        self.assertEqual(len(cache), 1)
        cache.set("foo", (None, "python"))
        self.assertEqual(self.cache_get("foo"), "python")
        self.assertEqual(cache.size, 6)
        self.assertEqual(len(cache), 1)

    def testDelete(self):
        c = self.cache
        c.set("foo", (None, "bar"))
        self.assertEqual(len(c), 1)
        data = self.cache_get("foo")
        self.assertEqual(data, "bar")
        self.checkCacheConsistent()
        del c["foo"]
        self.assertEqual(len(c), 0)

    def testClear(self):
        self.cache.set("foo", (None, "foo"))
        self.failUnlessEqual(len(self.cache), 1)
        self.cache.clear()
        self.failUnlessEqual(len(self.cache), 0)


class TestPurge(Tester):

    _cache_params_ = {'enable_background_purging':True}

    skip_test_makers = ["DiskCacheMaker2"]

    def testPurge(self):
        self.cache.set("foo", (None, (1,2)))
        self.cache.set("foopy", (None, (1,2)))
        self.cache.set("bar", (None, (1,2)))
        self.cache.purge_startswith("foo")
        time.sleep(0.5)
        self.failUnlessEqual(len(self.cache), 1)

    def testPurgeEmpty(self):
        self.cache.purge_startswith("foo")
        time.sleep(0.5)
        self.failUnlessEqual(len(self.cache), 0)


class TestLimitedSizeCache(Tester):

    _cache_params_ = {'max_size':5}

    def testEvictionSimple(self):
        each_size = (self._cache_params_['max_size'] / 2) + 1 # so 2 items will not fit.
        cache = self.cache
        cache.set("a", (None, "a" * each_size))
        time.sleep(0.01) # make sure we get a new timestamp
        self.assertEqual(self.cache_get("a"), "a" * each_size)
        cache.set("b", (None, "b" * each_size))
        self.assertEqual(self.cache_get("b"), "b" * each_size)
        # A should have been evicted.
        self.assertRaises(KeyError, self.cache_get, "a")
        self.assertEqual(len(cache), 1)

    def testEvictionOrder(self):
        each_size = (self._cache_params_['max_size'] / 3) + 1 # so 3 items will not fit.
        cache = self.cache
        cache.set("a", (None, "a" * each_size))
        time.sleep(0.02) # make sure we get a new timestamp
        cache.set("b", (None, "b" * each_size))
        time.sleep(0.02) # make sure we get a new timestamp
        cache.set("c", (None, "c" * each_size))
        # A was last in and last accessed - it should go.
        self.assertInCache("b", "c")
        self.assertNotInCache("a")
        # Now access 'b' - that should prevent it being evicted before 'c'
        time.sleep(0.02) # make sure we get a new 'accessed' timestamp
        self.cache_get('b')
        # Put 'a' back in to force the new eviction
        cache.set("a", (None, "a" * each_size))
        self.assertInCache("a", "b")
        self.assertNotInCache("c")


class TestNoAccessedCache(Tester):

    _cache_params_ = {'track_accessed':False, 'max_size':5}

    def testEvictionOrder(self):
        # As above, except "last accessed" is not taken into consideration.
        each_size = (self._cache_params_['max_size'] / 3) + 1 # so 3 items will not fit.
        cache = self.cache
        cache.set("a", (None, "a" * each_size))
        time.sleep(0.02) # make sure we get a new timestamp
        cache.set("b", (None, "b" * each_size))
        time.sleep(0.02) # make sure we get a new timestamp
        cache.set("c", (None, "c" * each_size))
        # A was last in - it should go.
        self.assertInCache("b", "c")
        self.assertNotInCache("a")
        # Now access 'b' - that should *not* prevent it being evicted before 'c'
        time.sleep(0.02) # make sure we get a new 'accessed' timestamp
        self.cache_get('b')
        # Put 'a' back in to force the new eviction
        cache.set("a", (None, "a" * each_size))
        self.assertInCache("a", "c")
        self.assertNotInCache("b")


# Test provider - only accepts ints (so we can easily check for bad keys)
# and fails to validate all odd numbered items.
# The data is the size of the key, so you can test large/small items.
class cacheProvider:

    def provide(self, key):
        try:
            size = int(key)
        except ValueError:
            raise KeyError
        data = "x" * size
        n = now()
        return key, metadata(
            len(data), n, t_stale = n + datetime.timedelta(seconds=0.25)), data

    def validate(self, key, meta, data, *args, **kw):
        if int(key) % 10 == 0:
            new_meta = copy.copy(meta)
            new_meta.size = meta.size * 2
            raise ValidationGotNewItem(key, new_meta, 'x' * new_meta.size)
        if int(key) % 2:
            raise KeyError, key
        n = now()
        return metadata(
            meta.size, n, t_stale = n + datetime.timedelta(seconds=0.25))


class TestProvider(Tester):

    _cache_params_ = {'provider':cacheProvider()}

    def testSimple(self):
        self.assertEqual(self.cache_get("0"), "")
        self.assertEqual(self.cache_get("2"), "xx")
        self.assertRaises(KeyError, self.cache_get, "xxx")
        # First query for '10' should give us the 'normal' data.
        self.assertEqual(self.cache_get("10"), ("x" * 10))
        # Now sleep unitl 10 is stale, then refetch - we should get new
        # data courtesy of the ValidationGotNewItem exception.
        time.sleep(0.4)
        self.assertEqual(self.cache_get("10"), ("x" * 20))


class TestFileMaint(Tester):

    def testTooLong(self):
        cache = self.cache
        if not getattr(cache.data, "return_files", None):
            # skip test for this cache.
            return
        cache.data.MAX_FILE_DELETE_QUEUE_TIME = 1 # one second.
        cache.set("foo", (None, "bar"))
        f = self.cache.get("foo")
        cache.set("foo", (None, "new"))
        time.sleep(1.5)
        cache.should_maintain()

        if os.name!='nt':
            # skip test is it is not win
            return

        cache.maintain()
        # so - the cache should have failed, and gave up, on this file.
        # If we close it and call maintain(), it should still exist.
        f.close()
        cache.maintain()
        self.failUnless(os.path.isfile(f.name))

        # but now we need to delete it, else our cache validation code will
        # complain about the orphan (if its *not* a true orphan, or validation
        # code would then complain about the file being missing, so this is
        # safe)
        os.remove(f.name)

    def testTooMany(self):
        cache = self.cache
        if not getattr(cache.data, "return_files", None):
            # skip test for this cache.
            return
        if os.name!='nt':
            # skip test is it is not win
            return
        cache.data.MAX_FILE_DELETE_QUEUE = 1 # one file
        cache.set("foo", (None, "bar"))
        f1 = self.cache.get("foo")
        cache.set("foo2", (None, "bar"))
        f2 = self.cache.get("foo2")
        cache.set("foo", (None, "new"))
        cache.set("foo2", (None, "new"))
        cache.maintain()
        # so - the cache should have failed, and gave up on one of these files.
        f1.close()
        f2.close()
        cache.maintain()
        # exactly 1 of the files should remain.
        self.failUnless(os.path.isfile(f1.name) or os.path.isfile(f2.name))
        self.failIf(os.path.isfile(f1.name) and os.path.isfile(f2.name))
        # but now we need to delete it, else our cache validation code will
        # complain about the orphan (if its *not* a true orphan, or validation
        # code would then complain about the file being missing, so this is
        # safe)
        if os.path.isfile(f1.name):
            os.remove(f1.name)
        if os.path.isfile(f2.name):
            os.remove(f2.name)


# Deriving from TestProvider means we also get some standard tests on this
# cache - so we only need to test specific "too big".
# with special params.
class TestItemsTooBig(TestProvider):

    _cache_params_ = {'max_item_size':100}

    _cache_params_.update(TestProvider._cache_params_)

    def testTooBig(self):
        num = len(self.cache)
        # We should get the data OK.
        data = self.cache_get("200")
        self.assertEqual(data, "x" * 200)
        # but it should not be cached.
        self.assertEqual(num, len(self.cache))


class TestItemsWayTooBig(TestProvider):
    # No max item size - but items bigger than cache max!

    _cache_params_ = {'max_size':100}

    _cache_params_.update(TestProvider._cache_params_)

    def testWayTooBig(self):
        num = len(self.cache)
        # We should get the data OK.
        data = self.cache_get("200")
        self.assertEqual(data, "x" * 200)
        # but it should not be cached.
        self.assertEqual(num, len(self.cache))


class TestPersistTester(Tester):

    def testSimple(self):
        self.cache.set("foo", (None, "bar"))
        self.assertEqual(len(self.cache), 1)
        self.reOpen()
        self.assertEqual(self.cache_get("foo"), "bar")
        self.assertEqual(len(self.cache), 1)


# Classes that make caches for testing.
class SimpleCacheMaker(CacheMaker):

    def setUp(self):
        params = dict(self._cache_params_)
        if 'provider' in params:
            provider = params['provider']
            del params['provider']
        else:
            provider = SimpleCacheProvider()

        self.cache = Cache(
            provider, CacheStorage(), logger=logger, **params)

    def tearDown(self):
        self.checkCacheConsistent()
        self.cache.close()


class DiskCacheMaker(CacheMaker):

    def setUp(self):
        self.dirname = tempfile.mktemp()
        os.mkdir(self.dirname)
        params = dict(self._cache_params_)
        if 'provider' in params:
            provider = params['provider']
            del params['provider']
        else:
            provider = SimpleCacheProvider()
        self.cache = Cache(
            provider, self._makeStorage(), logger = logger, **params)

    def tearDown(self):
        self.checkCacheConsistent()
        self.cache.close()
        try:
            shutil.rmtree(self.dirname)
        except os.error, details:
            print "FAILED to remove the cache directory '%s' - %s" \
                   % (self.dirname, details)

    def _makeStorage(self):
        return DiskStorage(self.dirname, logger)

    def reOpen(self):
        self.checkCacheConsistent()
        self.cache.close()

        params = dict(self._cache_params_)
        if 'provider' in params:
            provider = params['provider']
            del params['provider']
        else:
            provider = SimpleCacheProvider()

        self.cache = Cache(
            provider, self._makeStorage(), logger = logger, **params)
        self.checkCacheConsistent()

    def checkCacheConsistent(self):
        CacheMaker.checkCacheConsistent(self)
        data_dir = self.cache.data.data_directory
        self.failUnless(os.path.isdir(data_dir), data_dir)
        num_files = len(os.listdir(data_dir))
        self.assertEqual(num_files, len(self.cache))


# Our tests do screwey things if the default pickle is used.
def _storage_load_(fp):
    return fp.read()


def _storage_dump_(data, fp):
    fp.write(data)


class DiskCacheMaker2(DiskCacheMaker):

    def _makeStorage(self):
        s = DiskCacheMaker._makeStorage(self)
        s._load_ = _storage_load_
        s._dump_ = _storage_dump_
        s.return_files = True
        return s

    def cache_get(self, key):
        f = self.cache.get(key)
        if hasattr(f, "read"):
            f = f.read()
        return f


def MakeTestClass(TestRunner, CacheMaker):
    name = TestRunner.__name__ + "-" + CacheMaker.__name__
    return new.classobj(name, (CacheMaker, TestRunner, unittest.TestCase), {})


tests = []
for o in globals().values():
    try:
        if issubclass(o, Tester):
            tests.append(o)
    except TypeError:
        pass


# And special cases.
TestPersist = MakeTestClass(TestPersistTester, DiskCacheMaker)
tests.remove(TestPersistTester)


# Now build the tests.
for runner in tests:
    for maker in (SimpleCacheMaker, DiskCacheMaker, DiskCacheMaker2):
        if maker.__name__ not in getattr(runner, "skip_test_makers", ""):
            k = MakeTestClass(runner, maker)
            globals()[k.__name__] = k


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(
        doctest.DocTestSuite(
            'enfold.gcache.stats',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    suite.addTest(
        doctest.DocTestSuite(
            'enfold.gcache.cache',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    suite.addTest(
        doctest.DocTestSuite(
            'enfold.gcache.utils',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    suite.addTest(
        doctest.DocTestSuite(
            'enfold.gcache.priqueue',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    return suite
