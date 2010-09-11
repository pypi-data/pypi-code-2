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
from interfaces import IBlogPresentationInfo
from layer import IZBlogDefaultLayer
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.interfaces.blog import IBlog

# import Zope3 packages
from zope.app.container.contained import Contained
from zope.component import adapts
from zope.interface import implements
from zope.proxy import ProxyBase, setProxiedObject
from zope.schema.fieldproperty import FieldProperty

# import local packages
from menu import DefaultSkinJsMenuItem
from ztfy.blog.browser.blog import BaseBlogIndexView

from ztfy.blog import _


BLOG_PRESENTATION_KEY = 'ztfy.blog.defaultskin.blog.presentation'


class BlogPresentationViewMenuItem(DefaultSkinJsMenuItem):
    """Blog presentation menu item"""

    title = _(" :: Presentation model...")


class BlogPresentation(Persistent, Contained):
    """Blog presentation infos"""

    implements(IBlogPresentationInfo)

    header_format = FieldProperty(IBlogPresentationInfo['header_format'])
    header_position = FieldProperty(IBlogPresentationInfo['header_position'])
    page_entries = FieldProperty(IBlogPresentationInfo['page_entries'])
    disqus_site_id = FieldProperty(IBlogPresentationInfo['disqus_site_id'])


class BlogPresentationAdapter(ProxyBase):

    adapts(IBlog)
    implements(IBlogPresentationInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(BLOG_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[BLOG_PRESENTATION_KEY] = BlogPresentation()
        setProxiedObject(self, presentation)


class BlogPresentationTargetAdapter(object):

    adapts(IBlog, IZBlogDefaultLayer)
    implements(IPresentationTarget)

    target_interface = IBlogPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class BlogIndexView(BaseBlogIndexView):
    """Blog index page"""

    def getTopics(self):
        page = int(self.request.form.get('page', 0))
        page_length = self.presentation.page_entries
        first = page_length * page
        last = first + page_length - 1
        pages = len(self.topics) / page_length
        if len(self.topics) % page_length:
            pages += 1
        return { 'topics': self.topics[first:last + 1],
                 'pages': pages,
                 'first': first,
                 'last': last,
                 'has_prev': page > 0,
                 'has_next': last < len(self.topics) - 1 }
