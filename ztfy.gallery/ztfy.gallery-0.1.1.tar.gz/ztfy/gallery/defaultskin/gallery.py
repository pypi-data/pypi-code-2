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
from z3c.template.interfaces import IPageTemplate
from zc import resourcelibrary

# import local interfaces
from ztfy.blog.browser.interfaces.paragraph import IParagraphRenderer
from ztfy.blog.browser.interfaces.skin import ITopicIndexView
from ztfy.blog.browser.site import ISiteManager
from ztfy.blog.defaultskin.layer import IZBlogDefaultLayer
from ztfy.gallery.interfaces import IGalleryParagraph, IGalleryParagraphRenderer, IGalleryManagerPaypalInfo

# import Zope3 packages
from zope.app import zapi
from zope.component import adapts
from zope.interface import implements

# import local packages
from ztfy.blog.defaultskin.paragraph import ParagraphRenderer
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.traversing import getParent

from ztfy.gallery import _


class GalleryParagraphRenderer(ParagraphRenderer):

    adapts(IGalleryParagraph, ITopicIndexView, IZBlogDefaultLayer)
    implements(IParagraphRenderer)

    def __init__(self, context, view, request):
        super(GalleryParagraphRenderer, self).__init__(context, view, request)
        self.adapter = zapi.queryMultiAdapter((self.context, self.request), IGalleryParagraphRenderer, self.context.renderer)

    def update(self):
        if self.adapter is not None:
            resourcelibrary.need('ztfy.blog.defaultskin.gallery')
            self.adapter.update()

    def render(self):
        if self.adapter is not None:
            return self.adapter.render()
        return _("{{ Missing renderer ! }}")


class GalleryImageBuyForm(TemplateBasedPage):

    def __call__(self):
        if self.template is None:
            template = zapi.getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)
        return self.template()

    @property
    def paypal(self):
        site = getParent(self.context, ISiteManager)
        return IGalleryManagerPaypalInfo(site)
