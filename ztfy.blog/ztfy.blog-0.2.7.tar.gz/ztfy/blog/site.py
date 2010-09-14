### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList

# import Zope3 interfaces

# import local interfaces
from interfaces.blog import IBlog
from interfaces.section import ISection
from interfaces.site import ISiteManager, ITreeViewContents

# import Zope3 packages
from zope.app.component.site import SiteManagerContainer
from zope.app.content import queryContentType
from zope.component import adapts
from zope.event import notify
from zope.interface import implements

# import local packages
from ordered import OrderedContainer
from skin import InheritedSkin
from ztfy.extfile.blob import BlobImage
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty
from ztfy.utils.site import NewSiteManagerEvent


class SiteManager(OrderedContainer, SiteManagerContainer, InheritedSkin):
    """Main site manager class"""

    implements(ISiteManager)

    title = I18nTextProperty(ISiteManager['title'])
    shortname = I18nTextProperty(ISiteManager['shortname'])
    description = I18nTextProperty(ISiteManager['description'])
    keywords = I18nTextProperty(ISiteManager['keywords'])
    heading = I18nTextProperty(ISiteManager['heading'])
    header = I18nImageProperty(ISiteManager['header'], klass=BlobImage, img_klass=BlobImage)
    illustration = I18nImageProperty(ISiteManager['illustration'], klass=BlobImage, img_klass=BlobImage)

    def __init__(self, *args, **kw):
        self._data = OOBTree()
        self._order = PersistentList()

    @property
    def content_type(self):
        return queryContentType(self).__name__

    def setSiteManager(self, sm):
        SiteManagerContainer.setSiteManager(self, sm)
        notify(NewSiteManagerEvent(self))

    def getVisibleContents(self):
        return [v for v in self.values() if getattr(v, 'visible', True)]

    def getVisibleSections(self):
        """See `ISectionContainer` interface"""
        return [v for v in self.getVisibleContents() if ISection.providedBy(v)]

    @property
    def blogs(self):
        return [v for v in self.values() if IBlog.providedBy(v)]


class SiteManagerTreeViewContentsAdapter(object):

    adapts(ISiteManager)
    implements(ITreeViewContents)

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        return self.context.values()
