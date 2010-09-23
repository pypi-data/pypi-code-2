# -*- coding: utf-8 -*-
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import ptc

from quintagroup.dropdownmenu.tests.layer import DropDownMenuLayer


class TestCase(ptc.PloneTestCase):
    layer = DropDownMenuLayer

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='quintagroup.dropdownmenu',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='quintagroup.dropdownmenu.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'menu.txt', package='quintagroup.dropdownmenu',
            test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='quintagroup.dropdownmenu',
        #    test_class=TestCase),

        ])
