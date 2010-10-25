# -*- coding: utf-8 -*-
"""Test harness"""

import doctest
import unittest
import grokcore.message

from zope.component.testlayer import ZCMLFileLayer
from zope.publisher.browser import TestRequest
from zope.security.management import newInteraction, endInteraction

class GrokcoreMessageLayer(ZCMLFileLayer):

    def setUp(self):
        ZCMLFileLayer.setUp(self)
        newInteraction(TestRequest())

    def tearDown(self):
        endInteraction()
        ZCMLFileLayer.tearDown(self)

def test_suite():
    suite = unittest.TestSuite()
    test = doctest.DocFileSuite(
        'README.txt', optionflags=doctest.ELLIPSIS)
    test.layer = GrokcoreMessageLayer(grokcore.message)
    suite.addTest(test)
    return suite
