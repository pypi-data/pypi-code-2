import unittest

from BTrees.IIBTree import IISet

import BooleanIndex

class Dummy(object):
    def __init__(self, docid, truth):
        self.id = docid
        self.truth = truth

class TestBooleanIndex(unittest.TestCase):
    def test_index_true(self):
        index = BooleanIndex.BooleanIndex('truth')
        obj = Dummy(1, True)
        index._index_object(obj.id, obj, attr='truth')
        self.failUnless(index._unindex.has_key(1))
        self.failUnless(index._index.has_key(1))

    def test_index_false(self):
        index = BooleanIndex.BooleanIndex('truth')
        obj = Dummy(1, False)
        index._index_object(obj.id, obj, attr='truth')
        self.failUnless(index._unindex.has_key(1))
        self.failIf(index._index.has_key(1))

    def test_index_missing_attribute(self):
        index = BooleanIndex.BooleanIndex('truth')
        obj = Dummy(1, True)
        index._index_object(obj.id, obj, attr='missing')
        self.assertFalse(1 in index._unindex)
        self.assertFalse(1 in index._index)

    def test_search_true(self):
        index = BooleanIndex.BooleanIndex('truth')
        obj = Dummy(1, True)
        index._index_object(obj.id, obj, attr='truth')
        obj = Dummy(2, False)
        index._index_object(obj.id, obj, attr='truth')

        res,idx = index._apply_index({'truth':True}, res=None)
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [1])

    def test_search_false(self):
        index = BooleanIndex.BooleanIndex('truth')
        obj = Dummy(1, True)
        index._index_object(obj.id, obj, attr='truth')
        obj = Dummy(2, False)
        index._index_object(obj.id, obj, attr='truth')

        res,idx = index._apply_index({'truth':False}, res=None)
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [2])

    def test_search_inputresult(self):
        index = BooleanIndex.BooleanIndex('truth')
        obj = Dummy(1, True)
        index._index_object(obj.id, obj, attr='truth')
        obj = Dummy(2, False)
        index._index_object(obj.id, obj, attr='truth')

        res,idx = index._apply_index({'truth':True}, res=IISet([]))
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [])

        res,idx = index._apply_index({'truth':True}, res=IISet([2]))
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [])

        res,idx = index._apply_index({'truth':True}, res=IISet([1]))
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [1])

        res,idx = index._apply_index({'truth':True}, res=IISet([1, 2]))
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [1])

        res,idx = index._apply_index({'truth':False}, res=IISet([1, 2]))
        self.failUnlessEqual(idx, ('truth',))
        self.failUnlessEqual(list(res), [2])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBooleanIndex))
    return suite
