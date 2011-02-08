##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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

from unittest import TestCase
from zope.authentication.interfaces import IAuthentication
from zope.browser.interfaces import ISystemErrorView
from zope.component import getUtility, getMultiAdapter
from zope.component.testlayer import ZCMLFileLayer
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.publisher.defaultview import getDefaultViewName
from zope.publisher.interfaces.http import IHTTPException
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import Unauthorized
import zope.errorview

browser_layer = ZCMLFileLayer(zope.errorview.tests)


class MockPrincipal(object):
    id = 'mock principal'


class MockAuthenticationUtility(object):
    implements(IAuthentication)  # this is a lie.

    status = None

    def unauthorized(self, principal_id, request):
        if self.status is not None:
            request.response.setStatus(self.status)


class TestErrorViews(TestCase):

    layer = browser_layer

    def setUp(self):
        self.request = TestRequest()

    def test_defaultname(self):
        self.assertEquals(
            getDefaultViewName(Exception(), self.request), 'index.html')
        error = NotFound(object(), self.request)
        self.assertEquals(
            getDefaultViewName(error, self.request), 'index.html')
        self.assertEquals(
            getDefaultViewName(
                Unauthorized(), self.request), 'index.html')

    def test_exceptionview(self):
        view = getMultiAdapter((Exception(), self.request), name='index.html')
        self.assertEquals(view(), 'A system error occurred.')
        self.assertEquals(self.request.response.getStatus(), 500)

    def test_notfoundview(self):
        error = NotFound(object(), self.request)
        view = getMultiAdapter((error, self.request), name='index.html')
        self.failUnless(IHTTPException.providedBy(view))
        self.assertEquals(view(), 'The requested resource can not be found.')
        self.assertEquals(self.request.response.getStatus(), 404)

    def test_unauthorizedview(self):
        self.request.setPrincipal(MockPrincipal())
        view = getMultiAdapter(
            (Unauthorized(), self.request), name='index.html')
        self.failUnless(IHTTPException.providedBy(view))
        self.assertEquals(
            view(), 'Access to the requested resource is forbidden.')
        self.assertEquals(self.request.response.getStatus(), 403)

        getUtility(IAuthentication).status = 401
        self.assertEquals(
            view(), 'Access to the requested resource is forbidden.')
        self.assertEquals(self.request.response.getStatus(), 401)

        getUtility(IAuthentication).status = 302
        self.assertEquals(view(), '')
        self.assertEquals(self.request.response.getStatus(), 302)

        getUtility(IAuthentication).status = 303
        self.assertEquals(view(), '')
        self.assertEquals(self.request.response.getStatus(), 303)
