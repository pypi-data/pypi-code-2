### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
from persistent.list import PersistentList
from persistent.dict import PersistentDict

# import Zope3 interfaces
from zope.app.authentication.interfaces import IPrincipalInfo

# import local interfaces

# import Zope3 packages
from zc.set import Set
from zope.app import zapi
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

# import local packages


def unproxied(value):
    """Remove security proxies from given value ; if value is a list or dict, all elements are unproxied"""
    if isinstance(value, (list, PersistentList)):
        result = []
        for v in value:
            result.append(unproxied(v))
    elif isinstance(value, (dict, PersistentDict)):
        result = value.copy()
        for v in value:
            result[v] = unproxied(value[v])
    elif isinstance(value, (set, Set)):
        result = []
        for v in value:
            result.append(unproxied(v))
    else:
        result = removeSecurityProxy(value)
    return result


class MissingPrincipal(object):

    implements(IPrincipalInfo)

    def __init__(self, id):
        self.id = id

    @property
    def title(self):
        return _("< missing principal %s>") % self.id

    @property
    def description(self):
        return _("This principal can't be found in any authentication utility...")


def getPrincipal(uid):
    principals = zapi.principals()
    try:
        return principals.getPrincipal(uid)
    except:
        return MissingPrincipal(uid)
