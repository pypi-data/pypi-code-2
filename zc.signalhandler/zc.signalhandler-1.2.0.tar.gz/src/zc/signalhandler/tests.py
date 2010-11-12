"""\
Test harness for zc.signalhandler.

"""
__docformat__ = "reStructuredText"

import unittest

from zope.testing import doctest


def sample_handler_1():
    print "handler 1"

def sample_handler_2():
    print "handler 2"


def test_suite():
    return unittest.TestSuite([
        doctest.DocTestSuite("zc.signalhandler.datatypes"),
        doctest.DocFileSuite("README.txt"),
        ])
