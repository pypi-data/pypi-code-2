# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import logging

from pesto.lrucache import LRUCache

def test_lru():
    c = LRUCache(5)
    c['a'] = 'a'
    c['b'] = 'b'
    c['c'] = 'c'
    c['d'] = 'd'
    c['e'] = 'e'

    assert c.tolist() == ['e','d','c','b','a']

    assert c['a'], 'a'
    assert c.tolist() == ['a','e','d','c','b']

    assert c['b'] == 'b'
    assert c.tolist() == ['b','a','e','d','c']

    assert c['c'] == 'c'
    assert c.tolist() == ['c','b','a','e','d']

    assert c['d'] == 'd'
    assert c.tolist() == ['d','c','b','a','e']

    assert c['e'] == 'e'
    assert c.tolist() == ['e','d','c','b','a']

def test_set_existing_key():
    c = LRUCache(5)
    c['yop'] = 1
    assert c['yop'] == 1
    c['yop'] = 2
    assert c['yop'] == 2

def test_cachesize():
    c = LRUCache(10)
    for ix in xrange(10):
        c[ix] = ix
        assert len(c) == ix + 1

    for ix in xrange(10, 100):
        c[ix] = ix
        assert len(c) <= 10

def test_purgelistener():

    purged = []
    def listener(p):
        map(purged.append, p)

    c = LRUCache(10, 4, listener)
    for ix in xrange(11):
        c[ix] = ix

    assert purged == [ (0,0), (1,1), (2,2), (3,3) ]

def test_purge_single():

    purged = []

    def listener(p):
        map(purged.append, p)

    c = LRUCache(4, 1, listener)
    c[0] = 0
    c[1] = 1
    c[2] = 2
    c[3] = 3
    assert purged == []
    c[4] = 4
    assert purged == [(0, 0)]

    dummy = c[1]
    dummy = c[2]

    c[5] = 5
    assert purged == [(0, 0), (3, 3)]


def test_delete():
    c = LRUCache(10)
    for ix in xrange(10):
        c[ix] = ix
        assert len(c) == ix + 1

    del c[1]
    assert len(c) == 9




