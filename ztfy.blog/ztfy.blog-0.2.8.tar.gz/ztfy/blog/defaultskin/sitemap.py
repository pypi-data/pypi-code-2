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
from interfaces import IContainerSitemapInfo
from ztfy.blog.interfaces.blog import IBlog
from ztfy.blog.interfaces.section import ISection
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.blog.interfaces.topic import ITopic
from ztfy.workflow.interfaces import IWorkflowContent

# import Zope3 packages

# import local packages
from ztfy.skin.page import TemplateBasedPage


class SiteManagerMapsIndexView(TemplateBasedPage):
    """Site manager sitemaps index view"""

    def __call__(self):
        self.update()
        return self.render()


def getValues(parent, context, output):
    output.append(context)
    contents = IContainerSitemapInfo(context, None)
    if contents is not None:
        for item in contents.values:
            getValues(context, item, output)


class SiteManagerSitemapView(TemplateBasedPage):
    """Site manager sitemap view"""

    def __call__(self):
        self.update()
        return self.render()

    def getContents(self):
        result = []
        getValues(None, self.context, result)
        return result
