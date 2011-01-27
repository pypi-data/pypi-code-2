##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL
from zope.viewlet import viewlet
from zope.app.component import hooks


class SiteURL(BrowserPage):

    def __call__(self):
        return absoluteURL(hooks.getSite(), self.request)


class ManagementViewSelector(BrowserPage):
    """Redirect to the view with the default view name."""

    def __call__(self):
        url = '.'
        # not this is a very ugly pattern because the adapter is just a 
        # name as string which doesn't provide the adaption pattern at all
        viewName = zope.component.getSiteManager(self.context).adapters.lookup(
            map(zope.interface.providedBy, (self.context, self.request)),
                IDefaultViewName)
        if viewName is not None:
            url = '%s/@@%s' % (absoluteURL(self.context, self.request),
                viewName)

        self.request.response.redirect(url)
        return u''


JQueryMin121JavaScriptViewlet = viewlet.JavaScriptViewlet('jquery-1.2.1.min.js')
ZAMJavaScriptViewlet = viewlet.JavaScriptViewlet('zam-0.0.1.js')
ZAMCSSViewlet = viewlet.CSSViewlet('zam.css')

DivMenuJavaScriptViewlet = viewlet.JavaScriptViewlet('divmenu-0.5.0.js')
DivMenuCSSViewlet = viewlet.CSSViewlet('divmenu.css')
