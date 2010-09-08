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
from z3c.language.switch.interfaces import II18n

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView
from ztfy.skin.interfaces import IBreadcrumbInfo

# import Zope3 packages
from zope.app import zapi

# import local packages
from ztfy.skin.viewlet import ViewletBase

from ztfy.blog import _


class BreadcrumbsViewlet(ViewletBase):

    viewname = ''

    @property
    def crumbs(self):
        result = []
        for parent in reversed([self.context, ] + zapi.getParents(self.context)):
            info = IBreadcrumbInfo((parent, self.request), None)
            if info is not None:
                result.append({ 'title': info.title,
                                'path': info.path })
            else:
                adapter = zapi.queryMultiAdapter((parent, self.request, self.__parent__), IDefaultView)
                if adapter is not None:
                    self.viewname = '/' + adapter.viewname
                result.append({ 'title': II18n(parent).queryAttribute('shortname', request=self.request) or
                                         zapi.getName(parent),
                                'path': '%s%s' % (zapi.absoluteURL(parent, request=self.request),
                                                  self.viewname) })
        return result
