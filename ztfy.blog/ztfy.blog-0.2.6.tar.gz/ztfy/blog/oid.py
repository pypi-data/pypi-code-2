### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.app.intid.interfaces import IIntIds

# import local interfaces
from interfaces import IUniqueID, IBaseContent

# import Zope3 packages
from zope.app import zapi
from zope.component import adapts
from zope.interface import implements

# import local packages

from ztfy.blog import _


class UniqueIDAdapter(object):

    adapts(IBaseContent)
    implements(IUniqueID)

    def __init__(self, context):
        self.context = context

    @property
    def oid(self):
        intids = zapi.getUtility(IIntIds)
        return hex(intids.queryId(self.context))
