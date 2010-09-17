##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unauthorized Exception

$Id: unauthorized.py 100273 2009-05-23 02:20:25Z shane $
"""
__docformat__ = 'restructuredtext'

from zope.publisher.interfaces.http import IHTTPException
from zope.interface import implements

class Unauthorized(object):

    implements(IHTTPException)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.unauthorized('basic realm="Zope"')
        return ''

    __str__ = __call__
