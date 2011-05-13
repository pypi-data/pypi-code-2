#! /usr/bin/env python

import unittest

import decotrace


class DecoTraceTests (unittest.TestCase):

    def setUp(self):
        self._trace_log = []
        self.traced = decotrace.TraceContext(self._trace_log.append)


    def _define_next_int(self):

        @self.traced
        def next_int(x):
            return x+1

        return next_int


    def test_simple_function(self):

        next_int = self._define_next_int()

        self.assertEqual(3, next_int(2))
        self.assertTraceLogIs(
            'next_int calling with (2)...',
            'next_int return 3',
            )


    def test_keyword_call_display(self):

        next_int = self._define_next_int()

        self.assertEqual(3, next_int(x=2))
        self.assertTraceLogIs(
            'next_int calling with (x=2)...',
            'next_int return 3',
            )


    def test_name_collisions(self):

        @self.traced
        def hello(name):
            return 'Hello, ' + name
        
        self.assertEqual('Hello, bob', hello(name='bob'))
        self.assertTraceLogIs(
            "hello calling with (name='bob')...",
            "hello return 'Hello, bob'",
            )


    def assertTraceLogIs(self, *entries):
        self.assertEqual(list(entries), self._trace_log)



if __name__ == '__main__':
    unittest.main()
