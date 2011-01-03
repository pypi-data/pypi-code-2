##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
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

from grokcore.site.interfaces import IApplication
from zope.component.hooks import getSite


def getApplication():
    """Return the nearest enclosing :class:`grok.Application`.

    Raises :exc:`ValueError` if no application can be found.
    """
    site = getSite()
    if IApplication.providedBy(site):
        return site
    # Another sub-site is within the application. Walk up the object
    # tree until we get to the an application.
    obj = site
    while obj is not None:
        if IApplication.providedBy(obj):
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")

