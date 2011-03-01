##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Grok utility functions.
"""
import urllib
from zope.component import getMultiAdapter
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import _safe as SAFE_URL_CHARACTERS

def url(request, obj, name=None, data={}):
    url = getMultiAdapter((obj, request), IAbsoluteURL)()
    if name is not None:
        url += '/' + urllib.quote(name.encode('utf-8'), SAFE_URL_CHARACTERS)
    if data:
        for k,v in data.items():
            if isinstance(v, unicode):
                data[k] = v.encode('utf-8')
            if isinstance(v, (list, set, tuple)):
                data[k] = [isinstance(item, unicode) and item.encode('utf-8')
                or item for item in v]
        url += '?' + urllib.urlencode(data, doseq=True)
    return url
