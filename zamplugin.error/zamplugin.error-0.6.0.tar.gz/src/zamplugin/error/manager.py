##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema

from zope.error.interfaces import IErrorReportingUtility
from zope.error.interfaces import ILocalErrorReportingUtility
from zamplugin.error import interfaces


class ErrorReportingUtilityManager(object):
    """Error reporting utility schema."""

    zope.interface.implements(interfaces.IErrorReportingUtilityManager)
    zope.component.adapts(ILocalErrorReportingUtility)

    def __init__(self, context):
        self.context = context

    @apply
    def keep_entries():
        def get(self):
            data = self.context.getProperties()
            return data['keep_entries']
        def set(self, value):
            data = self.context.getProperties()
            keep_entries = value
            copy_to_zlog = data['copy_to_zlog']
            ignored_exceptions = data['ignored_exceptions']
            self.context.setProperties(keep_entries, copy_to_zlog,
                ignored_exceptions)
        return property(get, set)

    @apply
    def copy_to_zlog():
        def get(self):
            data = self.context.getProperties()
            return data['copy_to_zlog']
        def set(self, value):
            data = self.context.getProperties()
            keep_entries = data['keep_entries']
            copy_to_zlog = value
            ignored_exceptions = data['ignored_exceptions']
            self.context.setProperties(keep_entries, copy_to_zlog,
                ignored_exceptions)
        return property(get, set)

    @apply
    def ignored_exceptions():
        def get(self):
            data = self.context.getProperties()
            return data['ignored_exceptions']
        def set(self, value):
            data = self.context.getProperties()
            keep_entries = data['keep_entries']
            copy_to_zlog = data['copy_to_zlog']
            ignored_exceptions = value
            self.context.setProperties(keep_entries, copy_to_zlog,
                ignored_exceptions)
        return property(get, set)
