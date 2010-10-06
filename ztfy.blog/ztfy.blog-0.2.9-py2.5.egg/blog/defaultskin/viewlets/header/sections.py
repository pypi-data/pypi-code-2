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
import copy

# import Zope3 interfaces
from zope.publisher.interfaces.browser import IBrowserSkinType

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from zc import resourcelibrary
from zope.app import zapi
from zope.publisher.browser import applySkin

# import local packages
from ztfy.skin.viewlet import ViewletBase
from ztfy.utils.traversing import getParent


class SectionsListViewlet(ViewletBase):

    def update(self):
        super(SectionsListViewlet, self).update()
        resourcelibrary.need('ztfy.jquery.alerts')

    @property
    def sections(self):
        site = getParent(self.context, ISiteManager, allow_context=True)
        if site is not None:
            parents = zapi.getParents(self.context) + [self.context, ]
            for section in site.getVisibleContents():
                yield { 'section': section,
                        'selected': section in parents }

    @property
    def manage_url(self):
        skin = zapi.queryUtility(IBrowserSkinType, 'ZBlog.BO')
        if skin is not None:
            fake = copy.copy(self.request)
            applySkin(fake, skin)
        adapter = zapi.queryMultiAdapter((self.context, fake, self.__parent__), IDefaultView)
        if adapter is not None:
            return adapter.getAbsoluteURL()
