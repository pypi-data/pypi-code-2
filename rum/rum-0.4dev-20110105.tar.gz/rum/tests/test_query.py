# -*- coding: utf-8 -*-
from unittest import TestCase
from rum.query import *


class TestQuery(TestCase):
    def test_unicode_as_qs(self):
        q = Query(eq('fruit', u'Melón'))
        expected = 'q.o=eq&q.a=Mel%C3%B3n&q.c=fruit'
        self.failUnlessEqual(q.as_qs(), expected)

    def test_unicode_repr(self):
        q = Query(eq('fruit', u'Melón'))
        expected = "Query(eq('fruit', u'Mel\\xf3n'), None, None, None, ())"
        self.failUnlessEqual(`q`, expected)

    def test_and_of_many(self):
        expr = and_([eq('n', 1), eq('b', 2), eq('c', 4)])
        expected = "and_([eq('n', 1), eq('b', 2), eq('c', 4)])"
        self.failUnlessEqual(`expr`, expected)
    
    
    def test_query_in_and_more(self):
        expr = Query(and_(in_(1, [1, 2, 3]), eq(9,9)))
        expected ='Query(and_(in_(1, [1, 2, 3]), eq(9, 9)), None, None, None, ())'
        self.failUnlessEqual(`expr`, expected)
        expr = Query.from_dict(expr.as_dict())
        self.failUnlessEqual(`expr`, expected)
