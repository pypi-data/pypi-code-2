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

import zope.component
import zope.traversing.api
import zope.publisher.interfaces
from zope.proxy import sameProxiedObjects
from zope.traversing.interfaces import TraversalError


def getIconURL(item, request, name='icon'):
    url = ''
    icon = zope.component.queryMultiAdapter((item, request), name=name)
    if icon is not None:
        try:
            url = icon.url()
        except TraversalError:
            return url
    return url


def isChildOf(child, parent):
    """Check if object is a child of the parent."""
    try:
        if parent in zope.traversing.api.getParents(child):
            return True
        else:
            return False
    except TypeError, e:
        # could be a not locatable NotFound object
        return False

def getParentsFromContextToObject(context, obj):
    """Returns a list starting with the given context's parent followed by
    each of its parents till we reach the object.

    If the child object is not a child of the parent a empty list
    will return.
    """
    # this is a very bad situation. The context could be a NotFound error.
    # Such NotFound objects provide a LocationProxy with the site as parent
    # even if we don't allow the site in our possible parent chain. So skip it.
    if zope.publisher.interfaces.INotFound.providedBy(context):
        return []

    if not isChildOf(context, obj):
        return []
    
    if sameProxiedObjects(context, obj):
        return []

    parents = []
    w = context

    while 1:
        w = w.__parent__
        if sameProxiedObjects(w, obj):
            parents.append(w)
            break
        if w is None:
            break
        
        parents.append(w)

    return parents
