#! /usr/bin/env python

import unittest
import re

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
        self.checkTraceLog(
            r'next_int\(2\)...',
            r'next_int\(2\) -> 3',
            )


    def test_keyword_call_display(self):

        next_int = self._define_next_int()

        self.assertEqual(3, next_int(x=2))
        self.checkTraceLog(
            r'next_int\(x=2\)...',
            r'next_int\(x=2\) -> 3',
            )


    def test_exception(self):

        next_int = self._define_next_int()

        try:
            r = next_int('x')
        except TypeError:
            pass
        else:
            self.fail("Expected TypeError, but instead next_int('x') returns {0!r}".format(r))

        self.checkTraceLog(
            r"next_int\('x'\)...",
            r"next_int\('x'\) raising TypeError\(\"cannot concatenate 'str' and 'int' objects\",\)",
            )


    def test_name_collisions(self):

        @self.traced
        def hello(name):
            return 'Hello, ' + name
        
        self.assertEqual('Hello, bob', hello(name='bob'))
        self.checkTraceLog(
            r"hello\(name='bob'\)...",
            r"hello\(name='bob'\) -> 'Hello, bob'",
            )


    def test_method_decoration(self):

        class C (object):
            @self.traced
            def method(self, x):
                return x*2

        i = C()
        result = i.method(3)

        self.assertEqual(6, result)
        self.checkTraceLog(
            r"C\[@[0-9a-f]{8}\].method\(3\)...",
            r"C\[@[0-9a-f]{8}\].method\(3\) -> 6",
            )


    def test_log_id(self):

        class C (object):
            @self.traced
            def method(self):
                pass

        i = C()

        expectedHexId = '{0:08x}'.format(id(i))

        i.method()

        m = re.match(r'C\[@([0-9a-f]{8})\]', self._trace_log[0])
        self.failIf(m is None)

        loggedHexId = m.group(1)

        self.assertEqual(expectedHexId, loggedHexId)


    def checkTraceLog(self, *entries):
        self.assertEqual(len(entries), len(self._trace_log))

        for expected, actual in zip(entries, self._trace_log):
            pat = re.compile(expected)
            m = pat.match(actual)
            self.failIf(m is None, '{0!r} does not match {1!r}'.format(expected, actual))


if __name__ == '__main__':
    unittest.main()
