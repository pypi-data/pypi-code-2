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

from zope.authentication.interfaces import IAuthentication
from zope.component import getUtility
from zope.errorview.http import ExceptionViewBase, ExceptionView
from zope.errorview.http import UnauthorizedView
from zope.publisher.browser import BrowserPage

# XXX i18n-ing?


class ExceptionView(ExceptionViewBase, BrowserPage):

    def render(self):
        return u'A system error occurred.'


class NotFoundView(ExceptionViewBase, BrowserPage):

    def update(self):
        self.request.response.setStatus(404)

    def render(self):
        return u'The requested resource can not be found.'


class UnauthorizedView(UnauthorizedView, BrowserPage):

    def update(self):
        # Set the error status to 403 (Forbidden) in the case when we
        # don't challenge the user.
        self.request.response.setStatus(403)
        # Make sure that the response is not cacheable.
        self.request.response.setHeader(
            'Expires', 'Jan, 1 Jan 1970 00:00:00 GMT')
        self.request.response.setHeader(
            'Cache-Control', 'no-store, no-cache, must-revalidate')
        self.request.response.setHeader(
            'Pragma', 'no-cache')
        principal = self.request.principal
        getUtility(IAuthentication).unauthorized(principal.id, self.request)

    def render(self):
        if self.request.response.getStatus() not in (302, 303):
            return u'Access to the requested resource is forbidden.'
        return ''
