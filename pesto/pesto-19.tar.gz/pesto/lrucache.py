# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import threading

__docformat__ = 'restructuredtext en'
__version__ = '2'
__all__ = ['LRUCache']

class Node(object):
    """
    Node in a doubly-linked list
    """

    __slots__ = ['item', 'next', 'prev']

    def __init__(self, item, next, prev):
        self.item = item
        self.next = next
        self.prev = prev

    def __repr__(self):
        if self.next:
            next = self.next.item
        else:
            next = None
        if self.prev:
            prev = self.prev.item
        else:
            prev = None
        return repr((prev, self.item, next))


class LRUCache(dict):

    """
    Fixed size, least recently used (LRU) cache.

    This class implements (most) of the dict interface. When more items are
    added to the dict, than ``maxsize``, items are purged from the cache
    starting with the least recently used items.

    Usage of items is tracked through a doubly-linked list. As items are
    accessed they are moved to the front of the list. Items are purged from
    the end of the list.
    """

    def __init__(self, maxsize, purge_number=None, purge_listener=None):
        """
        Create a new Least Recently Used (LRU) caching object.

        maxsize
            the maximum number of items to store in this cache.

        purge_number
            the number of items to purge in one go.

        purge_listener
            a callable that will be invoked whenever items are
            purged from the cache, passing the list of (key,
            values) about to be deleted deleted. 
        """
        self.maxsize = maxsize
        self._first = None 
        self._last = None
        self.purge_listener = purge_listener
        if purge_number is None:
            purge_number = int(min(maxsize * 0.05, 100))
        self.purge_number = max(1, purge_number)
        self._lock = threading.Lock()

    def _moveToFront(self, node):
        """
        Move ``node`` to the front of the linked list
        """
        if self._first is node:
            return

        # Take node out of its list position
        try:
            node.prev.next = node.next
        except AttributeError: pass
        try:
            node.next.prev = node.prev
        except AttributeError: pass

        # If node is the last item, repoint _last
        if node is self._last:
            self._last = node.prev

        # And reinsert at the front
        try:
            self._first.prev = node
        except AttributeError: pass

        node.next = self._first
        node.prev = None
        self._first = node

    def __setitem__(self, key, value):
        self._lock.acquire()
        try:
            # Push node in at front of linked list
            try:
                oldval, node = super(LRUCache, self).__getitem__(key)
                self._moveToFront(node)
                super(LRUCache, self).__setitem__(key, (value, node))
            except KeyError:
                node = Node(key, self._first, None)
                if self._first:
                    self._first.prev = node

                if self._last is None:
                    self._last = node
                self._first = node
                super(LRUCache, self).__setitem__(key, (value, self._first))

            # Purge the cache if necessary
            if len(self) > self.maxsize:
                newlast = self._last
                if self.purge_listener is not None:
                    todel = []
                    for ix in xrange(self.purge_number):
                        todel.append((newlast.item, super(LRUCache, self).__getitem__(newlast.item)[0]))
                        super(LRUCache, self).__delitem__(newlast.item)
                        newlast = newlast.prev
                    self.purge_listener(todel)
                else:
                    for ix in xrange(self.purge_number):
                        super(LRUCache, self).__delitem__(newlast.item)
                        newlast = newlast.prev

                self._last = newlast
                if self._last:
                    self._last.next = None
        finally:
            self._lock.release()

    def __getitem__(self, key):
        self._lock.acquire()
        try:
            value, node = super(LRUCache, self).__getitem__(key)
            self._moveToFront(node)
            return value
        finally:
            self._lock.release()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __delitem__(self, key):
        self._lock.acquire()
        try:
            value, node = super(LRUCache, self).__getitem__(key)
            # Take node out of its list position
            if node.prev is not None:
                node.prev.next = node.next
            if node.next is not None:
                node.next.prev = node.prev
            if node is self._first:
                self._first = node.next
            if node is self._last:
                self._last = node.prev
            del node
            return super(LRUCache, self).__delitem__(key)
        finally:
            self._lock.release()

    def tolist(self):
        l = []
        node = self._first
        while node is not None:
            l.append(node.item)
            node = node.next
        return l

    def items(self):
        return [ (key, value[0]) for key, value in super(LRUCache, self).items() ]

    def iterkeys(self):
        return self.d.iterkeys()

    def iteritems(self):
        for item in super(LRUCache, self).iteritems():
            yield item[0], item[1][0]

    def itervalues(self):
        for item in super(LRUCache, self).itervalues():
            yield item[0]

    def __repr__(self):
        l = []
        node = self._first
        while node:
            l.append(node.item)
            node = node.next
        return repr(l)

    def debug(self):
        l = []
        node = self._first
        while node:
            if node is self._first and node is self._last:
                l.append("FL%r" % node)
            elif node is self._first:
                l.append("F%r" % node)
            elif node is self._last:
                l.append("L%r" % node)
            else:
                l.append(repr(node))
            node = node.next
        return ", ".join(l)


def check_linkedlistintegrity():
    # Checks list for correct backwards links (prev) and 
    # circular references and that this is maintained as the cache is manipulated
    c = LRUCache(30)
    def test_integrity():
        node = c._first
        prev = None
        seenbefore = Set()
        while node is not None:
            seenbefore.add(node)
            self.assertTrue(node.prev is prev)
            prev = node
            self.assertTrue(node.next not in seenbefore)
            node = node.next

    for ix, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
        c[ch] = ix
        test_integrity()

    for position in xrange(26):
        node = c._first
        # Select the ``position``th element from the linked list...
        for iy in xrange(position):
            node = node.next

        # ...and get it out of the cache, forcing the cache to
        # reorder itself
        dummy = c[node.item]
        test_integrity()
        self.assertEqual(len(c.tolist()), 26)

