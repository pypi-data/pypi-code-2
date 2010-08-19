##############################################################################
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
##############################################################################
"""
$Id: __init__.py 72087 2007-01-18 01:03:33Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.traversing.browser import absoluteURL

from z3c.template.template import getPageTemplate
from z3c.profiler.layer import IProfilerBrowserLayer
from z3c.profiler.interfaces import IMenuProvider


class MenuProvider(object):
    """Simple menu provider"""

    zope.interface.implements(IMenuProvider)
    zope.component.adapts(zope.interface.Interface, IProfilerBrowserLayer, 
        zope.interface.Interface)

    template = getPageTemplate()

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    @property
    def items(self):
        try:
            baseURL = absoluteURL(self.context, self.request)
        except TypeError, e:
            # not locatable
            baseURL = '.'
        return [
            {'name': 'Profile',
             'css' :'',
             'url': '%s/doProfile' % baseURL},
            {'name': 'Help',
             'css' :'',
             'url': '%s/help.html' % baseURL}
            ]

    def update(self):
        pass

    def render(self):
        return self.template()
