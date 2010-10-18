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
"""Pluggable Authentication Utility implementation

$Id: authentication.py 113109 2010-06-04 11:54:46Z janwijbrand $
"""

import zope.interface
from zope import component
from zope.location.interfaces import ILocation
from zope.app.authentication import interfaces

### BBB using zope.pluggableauth
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import (
    IQueriableAuthenticator, IPluggableAuthentication)


class QuerySchemaSearchAdapter(object):
    """Performs schema-based principal searches on behalf of a PAU.

    Delegates the search to the adapted authenticator (which also provides
    IQuerySchemaSearch) and prepends the PAU prefix to the resulting principal
    IDs.
    """
    component.adapts(
        interfaces.IQuerySchemaSearch,
        IPluggableAuthentication)

    zope.interface.implements(
        ILocation,
        IQueriableAuthenticator,
        interfaces.IQuerySchemaSearch)

    def __init__(self, authplugin, pau):
        if (ILocation.providedBy(authplugin) and
            authplugin.__parent__ is not None):
            # Checking explicitly for the parent, because providing ILocation
            # basically means that the object *could* be located. It doesn't
            # say the object must be located.
            self.__parent__ = authplugin.__parent__
            self.__name__ = authplugin.__name__
        else:
            self.__parent__ = pau
            self.__name__ = ""
        self.authplugin = authplugin
        self.pau = pau
        self.schema = authplugin.schema

    def search(self, query, start=None, batch_size=None):
        for id in self.authplugin.search(query, start, batch_size):
            yield self.pau.prefix + id
