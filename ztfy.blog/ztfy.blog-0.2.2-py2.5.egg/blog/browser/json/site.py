### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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
from zope.copypastemove.interfaces import IObjectMover

# import local interfaces
from ztfy.blog.interfaces.container import IOrderedContainer

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher
from zope.app import zapi

# import local packages

from ztfy.blog import _


class SiteManagerView(MethodPublisher):
    """Site manager JSON-RPC view"""

    def changeParent(self, source, target):
        intids = zapi.getUtility(IIntIds)
        source = intids.getObject(source)
        target = intids.getObject(target)
        IObjectMover(source).moveTo(target)
        if IOrderedContainer.providedBy(target):
            IOrderedContainer(target).moveFirst(zapi.getName(source))
