##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZTAPI Tests"""
import doctest
import unittest
from zope.app.testing import placelesssetup
from zope.app import zapi
from zope.app.zapi.interfaces import IZAPI
from zope.interface.verify import verifyObject
from zope.proxy import removeAllProxies, isProxy

class TestIZAPI(unittest.TestCase):

    def test_izapi(self):
        """
        Ensure that the zapi module provides the IZAPI interface
        """

        from zope.app import zapi
        # deprecation proxies don't seem to always work with
        # verifyObject, so remove any proxies
        if isProxy(zapi):
            zapi = removeAllProxies(zapi)

        # we don't want to generate warnings for deprecated
        # attrs
        import zope.deprecation
        zope.deprecation.__show__.off()
        verifyObject(IZAPI, zapi)
        zope.deprecation.__show__.on()


def setUp(test):
    placelesssetup.setUp()

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestIZAPI),
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=placelesssetup.tearDown),
        ))
