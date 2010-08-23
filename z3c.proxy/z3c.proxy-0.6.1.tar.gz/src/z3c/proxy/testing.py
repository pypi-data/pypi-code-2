###############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: testing.py 115867 2010-08-23 06:16:25Z icemac $
"""
__docformat__ = 'restructuredtext'

import zope.interface
from zope.container.interfaces import IContainer
from zope.container.tests.test_icontainer import BaseTestIContainer as BT
from zope.container.tests.test_icontainer import DefaultTestData

from z3c.testing.app import InterfaceBaseTest
from z3c.proxy import interfaces
from z3c.proxy import container


# stub testing classes
class ISampleContainerProxy(IContainer):
    """Sample interface."""


class SampleContainerProxy(container.ContainerLocationProxy):
    """Sample implementation."""

    zope.interface.implements(ISampleContainerProxy)


class BaseTestIContainerLocationProxy(InterfaceBaseTest, BT):

    def getTestInterface(self):
        return interfaces.IContainerLocationProxy

    def makeTestData(self):
        return DefaultTestData()

    def getUnknownKey(self):
        return '10'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']

    def test_IContainer(self):
        proxy = self.makeTestObject()
        self.assertEqual(IContainer.providedBy(proxy), True)
