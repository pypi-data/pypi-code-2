# -*- coding: utf-8 -*-

import unittest

from Products.JYUDynaPage.tests.base import JYUDynaPageTestCase


class TestSetup(JYUDynaPageTestCase):
    def afterSetUp(self):
        pass
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

