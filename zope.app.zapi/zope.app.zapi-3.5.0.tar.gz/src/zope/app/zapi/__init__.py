##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Collection of many common api functions

Makes imports easier

$Id: __init__.py 120643 2011-03-01 12:01:08Z icemac $
"""
from zope.interface import moduleProvides
from zope.app.zapi.interfaces import IZAPI
moduleProvides(IZAPI)
__all__ = tuple(IZAPI)

from zope.component import *
from zope.security.proxy import isinstance
from zope.traversing.api import *
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.exceptions.interfaces import UserError
from zope.app.publisher.browser import getDefaultViewName
from zope.app.publisher.browser import queryDefaultViewName
from zope.app.interface import queryType

name = getName

def principals():
    from zope.authentication.interfaces import IAuthentication
    return getUtility(IAuthentication)
