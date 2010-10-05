##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Null resource.

$Id: null.py 82045 2007-11-30 11:40:12Z srichter $
"""
import zope.component
import zope.interface
from zope.app.http.interfaces import INullResource
from zope.location import location
from zope.traversing.browser import absoluteURL

from z3c.rest import rest

class NullResource(location.Location):
    """Object representing objects to be created by a `PUT`."""
    zope.interface.implements(INullResource)

    def __init__(self, container, name):
        self.__parent__ = self.container = container
        self.__name__ = self.name = name

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


class NullPUT(rest.RESTView):
    """Put handler for null resources"""

    def PUT(self):
        nullPut = zope.component.queryMultiAdapter(
            (self.context.container, self.request), name='NullPUT')
        if nullPut is None:
            # See RFC 2616, section 9.6
            self.request.response.setStatus(501)
            return

        newObj = nullPut.NullPUT(self.context)

        # See RFC 2616, section 9.6
        self.request.response.setStatus(201)
        self.request.response.setHeader(
            'Location', absoluteURL(newObj, self.request))
