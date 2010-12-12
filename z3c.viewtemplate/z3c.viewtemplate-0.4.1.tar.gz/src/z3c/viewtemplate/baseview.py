##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id: baseview.py 80223 2007-09-27 14:15:32Z dobe $
"""
__docformat__ = "reStructuredText"

from zope import interface
from zope import component
from zope import event

from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserView

from z3c.viewtemplate.interfaces import ITemplatedContentProvider
from zope.contentprovider.interfaces import BeforeUpdateEvent

class TemplatedContentProvider(object):
    interface.implements(ITemplatedContentProvider)

    template = None

    def update(self):
        pass

    def render(self):
        if self.template is None:
            template = component.getMultiAdapter(
                    (self, self.request), IPageTemplate)
            return template(self)
        return self.template()


class BaseView(TemplatedContentProvider, BrowserView):

    def __call__(self):
        event.notify(BeforeUpdateEvent(self, self.request))
        self.update()
        return self.render()

