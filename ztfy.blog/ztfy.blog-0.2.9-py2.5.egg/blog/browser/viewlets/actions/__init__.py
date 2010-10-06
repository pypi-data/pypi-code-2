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

# import local interfaces
from interfaces import IActionsViewletManager, IZMIActionsViewletManager
from ztfy.blog.browser.interfaces import IDefaultView
from ztfy.blog.layer import IZTFYBlogLayer

# import Zope3 packages
from zope.app import zapi
from zope.interface import implements

# import local packages
from ztfy.skin.menu import MenuItem
from ztfy.skin.viewlet import WeightViewletManagerBase

from ztfy.blog import _


class BackToFrontMenu(MenuItem):

    title = _("Back to front-office")

    @property
    def url(self):
        result = self.viewURL
        if not result:
            return zapi.absoluteURL(self.context, self.request)
        elif result.startswith('/'):
            return result
        else:
            return '%s/%s' % (zapi.absoluteURL(self.context, self.request), result)

    @property
    def viewURL(self):
        adapter = zapi.queryMultiAdapter((self.context, IZTFYBlogLayer, self.__parent__), IDefaultView)
        if adapter is not None:
            return adapter.viewname
        return ''


class ActionsViewletManager(WeightViewletManagerBase):

    implements(IActionsViewletManager)


class ZMIActionsViewletManager(WeightViewletManagerBase):

    implements(IZMIActionsViewletManager)
