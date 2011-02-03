##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = 'restructuredtext'

from zope.component.interfaces import ComponentLookupError
from zope.traversing import api
from zope.traversing.interfaces import TraversalError
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.namespace import SimpleHandler
from zope.app.applicationcontrol.interfaces import IApplicationControl


class etc(SimpleHandler):

    def traverse(self, name, ignored):
        """Fix IApplicationControl lookup. 
        
        The original application control object doesn't use the real root as
        __parent__, this ends in a mess if it comes to menu concepts.
        TODO: We can get rid of this package if we fix the bad __parent__ setup
        in the following zope core packages zope.app.applicationcontrol and 
        zope.traversing.namespace
        """
        ob = self.context

        if (name in ('process', 'ApplicationController')
            and IContainmentRoot.providedBy(ob)):
            root = api.getRoot(self.context)
            return IApplicationControl(root)

        if name not in ('site',):
            raise TraversalError(ob, name)

        method_name = "getSiteManager"
        method = getattr(ob, method_name, None)
        if method is None:
            raise TraversalError(ob, name)
        try:
            return method()
        except ComponentLookupError:
            raise TraversalError(ob, name)
