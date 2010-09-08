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
from hurry.workflow.interfaces import IWorkflowState
from ztfy.blog.browser.interfaces import IDefaultView
from ztfy.blog.interfaces import STATUS_DELETED
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
        state = IWorkflowState(self.context, None)
        if (state is None) or (state.getState() != STATUS_DELETED):
            for parent in reversed([self.context, ] + zapi.getParents(self.context)):
                value = None
                info = IBreadcrumbInfo((parent, self.request), None)
                if info is not None:
                    if info.visible:
                        value = { 'title': info.title,
                                  'path': info.path }
                else:
                    visible = getattr(parent, 'visible', True)
                    if visible:
                        name = II18n(parent).queryAttribute('shortname', request=self.request)
                        if name:
                            adapter = zapi.queryMultiAdapter((parent, self.request, self.__parent__), IDefaultView)
                            if (adapter is not None) and adapter.viewname:
                                self.viewname = '/' + adapter.viewname
                            value = { 'title': name,
                                      'path': '%s%s' % (zapi.absoluteURL(parent, request=self.request),
                                                        self.viewname) }
                if value:
                    if result and (value['title'] == result[-1]['title']):
                        result[-1] = value
                    else:
                        result.append(value)
        return result
