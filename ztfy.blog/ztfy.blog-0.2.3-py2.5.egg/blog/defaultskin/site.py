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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from interfaces import ISiteManagerPresentationInfo
from layer import IZBlogDefaultLayer
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from zope.app.container.contained import Contained
from zope.component import adapts
from zope.interface import implements
from zope.proxy import ProxyBase, setProxiedObject
from zope.schema.fieldproperty import FieldProperty

# import local packages
from menu import DefaultSkinJsMenuItem
from ztfy.blog.browser.site import BaseSiteManagerIndexView
from ztfy.i18n.property import I18nTextProperty
from ztfy.workflow.interfaces import IWorkflowContent

from ztfy.blog import _


SITE_MANAGER_PRESENTATION_KEY = 'ztfy.blog.defaultskin.presentation'


class SiteManagerPresentationViewMenuItem(DefaultSkinJsMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")


class SiteManagerPresentation(Persistent, Contained):
    """Site manager presentation infos"""

    implements(ISiteManagerPresentationInfo)

    header_format = FieldProperty(ISiteManagerPresentationInfo['header_format'])
    header_position = FieldProperty(ISiteManagerPresentationInfo['header_position'])
    main_blogs = FieldProperty(ISiteManagerPresentationInfo['main_blogs'])
    nb_entries = FieldProperty(ISiteManagerPresentationInfo['nb_entries'])
    owner = FieldProperty(ISiteManagerPresentationInfo['owner'])
    owner_mailto = FieldProperty(ISiteManagerPresentationInfo['owner_mailto'])
    signature = I18nTextProperty(ISiteManagerPresentationInfo['signature'])
    disqus_site_id = FieldProperty(ISiteManagerPresentationInfo['disqus_site_id'])


class SiteManagerPresentationAdapter(ProxyBase):

    adapts(ISiteManager)
    implements(ISiteManagerPresentationInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(SITE_MANAGER_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[SITE_MANAGER_PRESENTATION_KEY] = SiteManagerPresentation()
        setProxiedObject(self, presentation)


class SiteManagerPresentationTargetAdapter(object):

    adapts(ISiteManager, IZBlogDefaultLayer)
    implements(IPresentationTarget)

    target_interface = ISiteManagerPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SiteManagerIndexView(BaseSiteManagerIndexView):
    """Site manager index page"""

    @property
    def topics(self):
        blogs = self.presentation.main_blogs
        if not blogs:
            return []
        topics = []
        [topics.extend(blog.getVisibleTopics()) for blog in blogs if blog.visible]
        topics.sort(key=lambda x: IWorkflowContent(x).publication_effective_date, reverse=True)
        return topics[:self.presentation.nb_entries]
