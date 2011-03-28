# -*- coding: utf-8 -*-

"""This module contains several test cases that is used to test the
correctness of the XML output.
"""

import unittest


class EmptyTestCase(unittest.TestCase):
    pass

class SuccessfulTestCase(unittest.TestCase):
    def test_success(self):
        print 'some text 何'

class FailedTestCase(unittest.TestCase):
    def test_failure(self):
        import sys
        print >> sys.stderr , 'another text 何'
        self.assertTrue(None)

class ErrordTestCase(unittest.TestCase):
    def test_errord(self):
        None + 1

class MixedTestCase(unittest.TestCase):
    def test_success(self):
        print 'some text 何'
    
    def test_failure(self):
        import sys
        print >> sys.stderr , 'another text 何'
        self.assertTrue(None)
    
    def test_errord(self):
        None + 1
