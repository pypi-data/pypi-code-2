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

# import local interfaces
from hurry.workflow.interfaces import IWorkflowState
from ztfy.blog.interfaces.container import IOrderedContainer

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher
from zope.app import zapi

# import local packages
from ztfy.blog.workflow import STATUS_DRAFT

from ztfy.blog import _


class ContainerView(MethodPublisher):
    """Default container JSON-RPC view"""

    def remove(self, id):
        intids = zapi.getUtility(IIntIds)
        target = intids.getObject(id)
        state = IWorkflowState(target, None)
        if (state is not None) and (state.getState() != STATUS_DRAFT):
            raise Exception, _("Only draft contents can be removed !")
        parent = zapi.getParent(target)
        del parent[zapi.getName(target)]
        return id


class OrderedContainerView(MethodPublisher):
    """Ordered container JSON-RPC view"""

    interface = None

    def updateOrder(self, ids):
        container = IOrderedContainer(self.context)
        container.updateOrder(ids, self.interface)
