#!/usr/bin/env python
"""
txriak trial test file.
txriak _must_ be on your PYTHONPATH

Copyright (c) 2010-2011 Appropriate Solutions, Inc. All rights reserved.
See txriak.LICENSE for details.
"""

import os
import sys
import json
import random
from twisted.trial import unittest
from twisted.python import log
from twisted.internet import defer

VERBOSE = False

# Since dev directory is not on path, force our parent
# directory onto python path.
PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PATH)
import riak

log.startLogging(sys.stderr)


RIAK_CLIENT_ID = 'TEST'
BUCKET = 'bucket'


def randint():
    """Generate nice random int for our test."""
    return random.randint(1, 999999)


@defer.inlineCallbacks
def cleanup_bucket(keys):
    """
    Delete objects defined by passed-in key.
    Bucket we're working with is global.
    Objects may not exist, and this is ok.
    """
    client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
    bucket = client.bucket(BUCKET)

    for key in keys:
        if VERBOSE:
            log.msg('deleting: %s' % key)
        obj = yield bucket.get(key)
        yield obj.delete()

    yield bucket.set_allow_multiples(False)


class RiakTestCase1(unittest.TestCase):
    """
    trial unit tests.
    """

    @defer.inlineCallbacks
    def tearDown(self):
        """delete all the bucket objects we might be using"""
        keys = ['foo', 'foo1', 'foo2', 'bar', 'baz', 'ba_foo1'
                'foo1', 'foo2', 'foo3', 'blue_foo1']
        yield cleanup_bucket(keys)

    @defer.inlineCallbacks
    def test_add_and_delete(self):
        """Basic adds and deletes"""
        log.msg("*** add_and_delete")

        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo1", "test1")
        yield obj.store()

        self.assertEqual(obj.exists(), True)
        self.assertEqual(obj.get_data(), "test1")

        obj.set_data('bar1')
        yield obj.store()

        obj = yield bucket.get("foo1")
        self.assertEqual(obj.exists(), True)
        self.assertEqual(obj.get_data(), "bar1")

        yield obj.delete()

        obj = yield bucket.get("foo1")
        self.assertEqual(obj.exists(), False)
        log.msg("done add_and_delete")

    @defer.inlineCallbacks
    def test_list_keys(self):
        """Test listing all keys in bucket."""
        log.msg("*** list_keys")

        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo1", "test1")
        yield obj.store()
        obj1 = bucket.new("foo2", "test2")
        yield obj1.store()

        keys = yield bucket.list_keys()
        self.assertEqual(sorted([u"foo1", u"foo2"]), sorted(keys))

    @defer.inlineCallbacks
    def test_purge_keys(self):
        """Test purging all keys in a bucket."""
        log.msg("*** purge_keys")
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo1", "test1")
        yield obj.store()
        obj1 = bucket.new("foo2", "test2")
        yield obj1.store()

        yield bucket.purge_keys()
        keys = yield bucket.list_keys()
        self.assertEqual([], keys)

    @defer.inlineCallbacks
    def test_list_buckets(self):
        """Test listing all buckets."""
        log.msg("*** list_buckets")

        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket1 = client.bucket("bucket1")
        obj1 = bucket1.new("foo1", "test1")
        yield obj1.store()

        bucket2 = client.bucket("bucket2")
        obj2 = bucket2.new("foo2", "test2")
        yield obj2.store()

        buckets = yield client.list_buckets()
        self.assertTrue(u"bucket1" in buckets)
        self.assertTrue(u"bucket2" in buckets)

        # Cleanup after ourselves
        yield obj1.delete()
        yield obj2.delete()

    @defer.inlineCallbacks
    def test_is_alive(self):
        """Can we ping the riak server."""
        log.msg('*** is_alive')
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        client_id = client.get_client_id()
        self.assertEqual(client_id, RIAK_CLIENT_ID)
        alive = yield client.is_alive()
        self.assertEqual(alive, True)
        log.msg('done is_alive')

    @defer.inlineCallbacks
    def test_store_and_get(self):
        """Store and get text data."""
        log.msg('*** store_and_get')
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket(BUCKET)
        data = 'blueprint'
        obj = bucket.new('blue_foo1', data)
        yield obj.store()
        del(obj)

        obj1 = yield bucket.get('blue_foo1')
        self.assertEqual(obj1.exists(), True)
        self.assertEqual(obj1.get_bucket().get_name(), BUCKET)
        self.assertEqual(obj1.get_key(), 'blue_foo1')
        self.assertEqual(obj1.get_data(), data)
        log.msg('done store_and_get')

    @defer.inlineCallbacks
    def test_binary_store_and_get(self):
        """store and get binary data."""

        log.msg('*** binary_store_and_get')
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket(BUCKET)

        # Store as binary, retrieve as binary, then compare...
        rand = str(randint())
        obj = bucket.new_binary('foo1', rand)
        yield obj.store()
        del(obj)

        obj = yield bucket.get_binary('foo1')
        self.assertEqual(obj.exists(), True)
        self.assertEqual(obj.get_data(), rand)
        del(obj)

        # Store as JSON, retrieve as binary, JSON-decode, then compare...
        data = [randint(), randint(), randint()]
        obj = bucket.new('foo2', data)
        yield obj.store()
        del(obj)

        obj = yield bucket.get_binary('foo2')
        self.assertEqual(data, json.loads(obj.get_data()))
        log.msg('done binary_store_and_get')

    @defer.inlineCallbacks
    def test_missing_object(self):
        """handle missing objects."""
        log.msg('*** missing_object')
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket(BUCKET)
        obj = yield bucket.get("missing")
        self.assertEqual(not obj.exists(), True)
        self.assertEqual(obj.get_data(), None)
        log.msg('done missing_object')

    @defer.inlineCallbacks
    def test_delete(self):
        """delete objects"""
        log.msg('*** delete')
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket(BUCKET)
        rand = randint()
        obj = bucket.new('foo', rand)
        yield obj.store()
        obj = yield bucket.get('foo')
        self.assertEqual(obj.exists(), True)
        yield obj.delete()
        yield obj.reload()
        self.assertEqual(obj.exists(), False)
        log.msg('done delete')

    @defer.inlineCallbacks
    def test_set_bucket_properties(self):
        """manipulate bucket properties"""
        log.msg('*** set_bucket_properties')
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket(BUCKET)
        # Test setting allow mult...
        yield bucket.set_allow_multiples(True)
        is_multiples = yield bucket.get_allow_multiples()
        self.assertEqual(is_multiples, True)
        # Test setting nval...
        yield bucket.set_n_val(3)
        n_val = yield bucket.get_n_val()
        self.assertEqual(n_val, 3)
        # Test setting multiple properties...
        yield bucket.set_properties({"allow_mult": False, "n_val": 2})
        is_multiples = yield bucket.get_allow_multiples()
        n_val = yield bucket.get_n_val()
        self.assertEqual(is_multiples, False)
        self.assertEqual(n_val, 2)
        log.msg('done set_bucket_properties')

    @defer.inlineCallbacks
    def test_siblings(self):
        """find siblings"""
        # Siblings works except for the store at the end.
        # Need to isolate and test that separately.
        log.msg('*** siblings')

        # Set up the bucket, clear any existing object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket('multiBucket')
        yield bucket.set_allow_multiples(True)
        obj = yield bucket.get('foo')
        yield obj.delete()

        obj = yield bucket.get('foo')
        self.assertEqual(obj.exists(), False)

        # Store the same object multiple times...
        for i in range(5):
            # for this to work, we must get a new RiakClient
            # on each pass and it must have a different client_id.
            # calling RiakClient without params uses randomly-generate id.
            client = riak.RiakClient()
            bucket = client.bucket('multiBucket')
            obj = bucket.new('foo', randint())
            yield obj.store()

        # Make sure the object has 5 siblings...
        self.assertEqual(obj.has_siblings(), True)
        self.assertEqual(obj.get_sibling_count(), 5)

        # Test get_sibling()/get_siblings()...
        siblings = yield obj.get_siblings()
        obj3 = yield obj.get_sibling(3)
        self.assertEqual(siblings[3].get_data(), obj3.get_data())

        # Resolve the conflict, and then do a get...
        obj3 = yield obj.get_sibling(3)
        yield obj3.store()
        yield obj.reload()
        self.assertEqual(obj.get_data(), obj3.get_data())

        # Clean up for next test...
        yield obj.delete()
        log.msg('done siblings')

    @defer.inlineCallbacks
    def test_javascript_source_map(self):
        """javascript mapping"""
        log.msg('*** javascript_source_map')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo", 2)
        yield obj.store()
        # Run the map...
        job = client \
                .add("bucket", "foo") \
                .map("function (v) { return [JSON.parse(v.values[0].data)]; }")
        result = yield job.run()
        self.assertEqual(result, [2])
        log.msg('done javascript_source_map')

    @defer.inlineCallbacks
    def test_javascript_named_map(self):
        """javascript mapping with named map"""
        log.msg('*** javascript_named_map')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo", 2)
        yield obj.store()
        # Run the map...
        job = client \
                .add("bucket", "foo") \
                .map("Riak.mapValuesJson")
        result = yield job.run()
        self.assertEqual(result, [2])
        log.msg('done javascript_named_map')

    @defer.inlineCallbacks
    def test_javascript_source_map_reduce(self):
        """javascript map reduce"""
        log.msg('*** javascript_source_map_reduce')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        yield bucket.new("foo", 2).store()
        yield bucket.new("bar", 3).store()
        yield bucket.new("baz", 4).store()
        # Run the map...
        job = client \
                .add("bucket", "foo") \
                .add("bucket", "bar") \
                .add("bucket", "baz") \
                .map("function (v) { return [1]; }") \
                .reduce("function(v) { return [v.length]; } ")
        result = yield job.run()
        self.assertEqual(result, [3])
        log.msg('done javascript_source_map_reduce')

    @defer.inlineCallbacks
    def test_javascript_named_map_reduce(self):
        """javascript map reduce by name"""
        log.msg('*** javascript_named_map_reduce')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        yield bucket.new("foo", 2).store()
        yield bucket.new("bar", 3).store()
        yield bucket.new("baz", 4).store()
        # Run the map...
        job = client \
                .add("bucket", "foo") \
                .add("bucket", "bar") \
                .add("bucket", "baz") \
                .map("Riak.mapValuesJson") \
                .reduce("Riak.reduceSum")
        result = yield job.run()
        self.assertEqual(result, [9])
        log.msg('done javascript_named_map_reduce')

    @defer.inlineCallbacks
    def test_javascript_key_filter_map_reduce(self):
        """javascript map/reduce using key filters"""
        log.msg("javascript map reduce with key filter")
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        yield bucket.new("foo", 2).store()
        yield bucket.new("bar", 3).store()
        yield bucket.new("baz", 4).store()
        # Run the map...
        job = client \
                .add({"bucket": "bucket",
                      "key_filters": [["starts_with", "ba"]]}) \
                .map("function (v) { return [1]; }") \
                .reduce(
            "function(v) { if(v.length) return [v.length]; else return []} ")
        result = yield job.run()
        self.assertEqual(result, [2])
        log.msg('done javascript_key_filter_map_reduce')

    def test_javascript_bucket_map_reduce(self):
        """javascript bucket map reduce"""
        log.msg('*** javascript_bucket_map_reduce')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket_name = "bucket_%s" % randint()
        bucket = client.bucket(bucket_name)
        bucket.new("foo", 2).store()
        bucket.new("bar", 3).store()
        bucket.new("baz", 4).store()
        # Run the map...
        job = client \
                .add(bucket.get_name()) \
                .map("Riak.mapValuesJson") \
                .reduce("Riak.reduceSum")
        result = yield job.run()
        self.assertEqual(result, [9])

    @defer.inlineCallbacks
    def test_javascript_arg_map_reduce(self):
        """javascript arguments map reduce"""
        log.msg('*** javascript_arg_map_reduce')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo", 2)
        obj.store()
        # Run the map...
        job = client \
                .add("bucket", "foo", 5) \
                .add("bucket", "foo", 10) \
                .add("bucket", "foo", 15) \
                .add("bucket", "foo", -15) \
                .add("bucket", "foo", -5) \
                .map("function(v, arg) { return [arg]; }") \
                .reduce("Riak.reduceSum")
        result = yield job.run()
        self.assertEqual(result, [10])
        log.msg('done javascript_arg_map_reduce')

    @defer.inlineCallbacks
    def test_erlang_map_reduce(self):
        """erlang map reduce"""
        log.msg('*** erlang_map_reduce')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo", 2)
        yield obj.store()

        obj = bucket.new("bar", 2)
        yield obj.store()

        obj = bucket.new("baz", 4)
        yield obj.store()

        # Run the map...
        job = client \
                .add("bucket", "foo") \
                .add("bucket", "bar") \
                .add("bucket", "baz") \
                .map(["riak_kv_mapreduce", "map_object_value"]) \
                .reduce(["riak_kv_mapreduce", "reduce_set_union"])
        result = yield job.run()
        self.assertEqual(len(result), 2)
        log.msg('done erlang_map_reduce')

    @defer.inlineCallbacks
    def test_map_reduce_from_object(self):
        """map reduce from an object"""
        log.msg('*** map_reduce_from_object')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        bucket.new("foo", 2).store()
        obj = yield bucket.get("foo")
        job = obj.map("Riak.mapValuesJson")
        result = yield job.run()
        self.assertEqual(result, [2])
        log.msg('done map_reduce_from_object')

    @defer.inlineCallbacks
    def test_store_and_get_links(self):
        """manipulate links"""
        # if we store with the basho test, we get this correctly.
        # so there's now something wrong with link storage.
        log.msg('*** store_and_get_links')

        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj = bucket.new("foo", 2) \
                .add_link(bucket.new("foo1")) \
                .add_link(bucket.new("foo2"), "tag") \
                .add_link(bucket.new("foo3"), "tag2!@#%^&*)")
        yield obj.store()
        del(obj)

        log.msg("Get the Links")
        obj = yield bucket.get("foo")
        links = obj.get_links()
        self.assertEqual(len(links), 3)
        log.msg('done store_and_get_links')

    @defer.inlineCallbacks
    def test_link_walking(self):
        """walk links"""
        log.msg('*** link_walking')
        # Create the object...
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")
        obj_1 = bucket.new("foo1", "test1")
        yield obj_1.store()

        obj_2 = bucket.new("foo2", "test2")
        yield obj_2.store()

        obj_3 = bucket.new("foo3", "test3")
        yield obj_3.store()

        obj = bucket.new("foo", 2) \
                .add_link(obj_1) \
                .add_link(obj_2, "tag") \
                .add_link(obj_3, "tag2!@#%^&*)")
        yield obj.store()
        obj = yield bucket.get("foo")
        job = obj.link("bucket")
        results = yield job.run()
        self.assertEqual(len(results), 3)
        results = yield obj.link("bucket", "tag").run()
        self.assertEqual(len(results), 1)
        log.msg('done link_walking')

    @defer.inlineCallbacks
    def test_meta_data_simple(self):
        """ensure we can get and set metadata"""
        log.msg('*** meta_data_simple')

        key = "foo1"
        key_data = "test1"

        # set up the bucket
        client = riak.RiakClient(client_id=RIAK_CLIENT_ID)
        bucket = client.bucket("bucket")

        # be sure object is deleted before we start
        obj = yield bucket.get(key)
        yield obj.delete()

        # now get a fresh new one
        obj = bucket.new(key, key_data)

        # see we can store and get back a header
        meta_key = 'this-is-a-test'
        meta_key1 = 'Fifty-Three'
        meta_data = 'ABCDEFG 123'
        obj.add_meta_data(meta_key, meta_data)
        metas = obj.get_all_meta_data()
        self.assertTrue(meta_key in metas)
        self.assertEqual(1, len(metas))

        # add second meta_data and get back both.
        # since they are stored as dictionary, we cannot
        # trus the order
        obj.add_meta_data(meta_key1, meta_data)
        metas = obj.get_all_meta_data()
        self.assertEqual(2, len(metas))
        self.assertTrue(meta_key in metas)
        self.assertTrue(meta_key1 in metas)

        # now delete one of the metas
        obj.remove_meta_data(meta_key)
        metas = obj.get_all_meta_data()
        self.assertFalse(meta_key in metas)
        self.assertTrue(meta_key1 in metas)
        self.assertEqual(1, len(metas))

        # store the object
        # since return body is true, the obj is refreshed
        yield obj.store()
        metas = obj.get_all_meta_data()

        # remember: twisted lowercases the headers!
        mk1_lc = meta_key1.lower()
        self.assertTrue(mk1_lc in metas)
        self.assertTrue(metas[mk1_lc] == meta_data)
        log.msg('done meta_data_simple')
