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
from datetime import datetime
from persistent import Persistent
from persistent.list import PersistentList

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from interfaces import IComment, IComments, ICommentsList, ICommentable
from interfaces import ICommentAddedEvent

# import Zope3 packages
from zope.component import adapts
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent

# import local packages
from ztfy.security.search import getPrincipal
from ztfy.utils.request import getRequest
from ztfy.utils.security import unproxied
from ztfy.utils.text import textToHTML
from ztfy.utils.timezone import gmtime

from ztfy.comment import _


class CommentAddedEvent(ObjectModifiedEvent):

    implements(ICommentAddedEvent)

    def __init__(self, object, comment):
        super(CommentAddedEvent, self).__init__(object)
        self.comment = comment


class Comment(Persistent):

    implements(IComment)

    def __init__(self, body, in_reply_to=None, renderer=None, tags=()):
        self.body = body
        self.body_renderer = renderer
        self.in_reply_to = unproxied(in_reply_to)
        if isinstance(tags, (str, unicode)):
            tags = tags.split(',')
        self.tags = set(tags)

    @property
    def date(self):
        return IZopeDublinCore(self).created

    def getAge(self):
        now = gmtime(datetime.utcnow())
        delta = now - self.date
        if delta.days > 60:
            return translate(_("%d months ago")) % int(round(delta.days * 1.0 / 30))
        elif delta.days > 10:
            return translate(_("%d weeks ago")) % int(round(delta.days * 1.0 / 7))
        elif delta.days > 2:
            return translate(_("%d days ago")) % delta.days
        elif delta.days == 2:
            return translate(_("the day before yesterday"))
        elif delta.days == 1:
            return translate(_("yesterday"))
        else:
            hours = int(round(delta.seconds * 1.0 / 3600))
            if hours > 1:
                return translate(_("%d hours ago")) % hours
            elif delta.seconds > 300:
                return translate(_("%d minutes ago")) % int(round(delta.seconds * 1.0 / 60))
            else:
                return translate(_("less than 5 minutes ago"))

    @property
    def principal_id(self):
        return IZopeDublinCore(self).creators[0]

    @property
    def principal(self):
        return getPrincipal(self.principal_id).title

    def render(self, request=None):
        if request is None:
            request = getRequest()
        return textToHTML(self.body, self.body_renderer, request)


class Comments(PersistentList):
    """Comments container class"""

    implements(ICommentsList)


COMMENTS_ANNOTATION_KEY = 'ztfy.comment'

class CommentsAdapter(object):

    adapts(ICommentable)
    implements(IComments)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        comments = annotations.get(COMMENTS_ANNOTATION_KEY)
        if comments is None:
            comments = annotations[COMMENTS_ANNOTATION_KEY] = Comments()
        self.comments = comments

    def getComments(self, tag=None):
        if not tag:
            return self.comments
        return [c for c in self.comments if tag in c.tags]

    def addComment(self, body, in_reply_to=None, renderer=None, tags=()):
        comment = Comment(body, in_reply_to, renderer, tags)
        notify(ObjectCreatedEvent(comment))
        self.comments.append(comment)
        notify(CommentAddedEvent(self.context, comment))
