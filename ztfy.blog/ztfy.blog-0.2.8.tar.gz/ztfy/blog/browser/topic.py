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
from hurry.workflow.interfaces import IWorkflowState
from z3c.language.switch.interfaces import II18n
from zope.app.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IZopeDublinCore
from zope.publisher.interfaces import NotFound

# import local interfaces
from interfaces import IDefaultView, ITopicAddFormMenuTarget
from interfaces.container import IContainerBaseView
from interfaces.container import IStatusColumn, IActionsColumn
from interfaces.container import IContainerTableViewStatusCell, IContainerTableViewActionsCell
from interfaces.skin import IEditFormButtons, ITopicIndexView
from site import ISiteManagerTreeView
from ztfy.blog.browser.interfaces.paragraph import IParagraphRenderer
from ztfy.blog.interfaces import STATUS_LABELS, STATUS_DRAFT, STATUS_PUBLISHED, STATUS_RETIRED, STATUS_ARCHIVED
from ztfy.blog.interfaces.topic import ITopic, ITopicInfo, ITopicContainer
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer
from ztfy.comment.interfaces import IComments
from ztfy.workflow.interfaces import IWorkflowTarget, IWorkflowContent

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from zope.app import zapi
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements

# import local packages
from container import OrderedContainerBaseView
from skin import BaseAddForm, BaseEditForm, BasePresentationEditForm, BaseIndexView
from ztfy.blog.browser.viewlets.properties import PropertiesViewlet
from ztfy.blog.topic import Topic
from ztfy.skin.menu import MenuItem
from ztfy.utils.security import getPrincipal
from ztfy.utils.timezone import tztime

from ztfy.blog import _


class TopicContainerContentsViewMenu(MenuItem):
    """Topics container contents menu"""

    title = _("Topics")


class TopicAddFormMenu(MenuItem):
    """Topics container add form menu"""

    title = _(" :: Add topic...")


class TopicTreeViewDefaultViewAdapter(object):

    adapts(ITopic, IZTFYBlogBackLayer, ISiteManagerTreeView)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@properties.html'

    def getAbsoluteURL(self):
        intids = zapi.getUtility(IIntIds)
        return '++oid++%d/%s' % (intids.register(self.context), self.viewname)


class TopicContainerContentsView(OrderedContainerBaseView):
    """Topics container contents view"""

    implements(ITopicAddFormMenuTarget)

    legend = _("Container's topics")
    cssClasses = { 'table': 'orderable' }

    @property
    def values(self):
        return ITopicContainer(self.context).topics


class TopicContainerTableViewCellStatus(object):

    adapts(ITopic, IZTFYBlogLayer, IContainerBaseView, IStatusColumn)
    implements(IContainerTableViewStatusCell)

    def __init__(self, context, request, view, table):
        self.context = context
        self.request = request
        self.view = view
        self.table = table

    @property
    def content(self):
        status = IWorkflowState(self.context).getState()
        if status == STATUS_DRAFT:
            klass = "ui-workflow ui-icon ui-icon-draft"
        elif status == STATUS_RETIRED:
            klass = "ui-workflow ui-icon ui-icon-retired"
        elif status == STATUS_ARCHIVED:
            klass = "ui-workflow ui-icon ui-icon-archived"
        else:
            klass = "ui-workflow ui-icon ui-icon-published"
        if klass:
            return '<span class="%s"></span> %s' % (klass,
                                                    translate(STATUS_LABELS[status], context=self.request))
        return ''


class TopicContainerTableViewCellActions(object):

    adapts(ITopic, IZTFYBlogLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        status = IWorkflowState(self.context).getState()
        if status == STATUS_DRAFT:
            klass = "ui-workflow ui-icon ui-icon-trash"
            intids = zapi.getUtility(IIntIds)
            return '''<span class="%s" title="%s" onclick="$.ZBlog.container.remove(%s,this);"></span>''' % (klass,
                                                                                                             translate(_("Delete topic"), context=self.request),
                                                                                                             intids.register(self.context))
        return ''


class TopicAddForm(BaseAddForm):

    implements(ITopicAddFormMenuTarget)

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new topic")

    fields = field.Fields(ITopicInfo).omit('publication_year', 'publication_month') + \
             field.Fields(IWorkflowTarget)

    def updateWidgets(self):
        super(TopicAddForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    def create(self, data):
        topic = Topic()
        topic.shortname = data.get('shortname', {})
        topic.workflow_name = data.get('workflow_name')
        return topic

    def add(self, topic):
        self.context.addTopic(topic)

    def nextURL(self):
        return '%s/@@contents.html' % zapi.absoluteURL(self.context, self.request)


class TopicEditForm(BaseEditForm):

    legend = _("Topic properties")

    fields = field.Fields(ITopicInfo).omit('publication_year', 'publication_month')
    buttons = button.Buttons(IEditFormButtons)

    def updateWidgets(self):
        super(TopicEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(TopicEditForm, self).handleApply(self, action)

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZBlog.form.reset(this.form);'


class TopicPresentationEditForm(BasePresentationEditForm):
    """Blog presentation edit form"""

    legend = _("Edit topic presentation properties")

    parent_interface = ITopic


class TopicPropertiesViewlet(PropertiesViewlet):
    """Topic properties viewlet"""

    @property
    def contributors(self):
        uids = IZopeDublinCore(self.context).creators[1:]
        return ', '.join((getPrincipal(uid).title for uid in uids))

    @property
    def status_date(self):
        return tztime(IWorkflowContent(self.context).state_date)

    @property
    def status_principal(self):
        return getPrincipal(IWorkflowContent(self.context).state_principal)

    @property
    def first_publication_date(self):
        return tztime(IWorkflowContent(self.context).first_publication_date)

    @property
    def publication_dates(self):
        content = IWorkflowContent(self.context)
        return (tztime(content.publication_effective_date), tztime(content.publication_expiration_date))

    @property
    def history(self):
        comments = IComments(self.context)
        return comments.getComments('__workflow__')


class BaseTopicIndexView(BaseIndexView):
    """Base topic index view"""

    implements(ITopicIndexView)

    def update(self):
        if not IWorkflowContent(self.context).isVisible():
            raise NotFound(self.context, self.__name__, self.request)
        super(BaseTopicIndexView, self).update()
        self.renderers = [renderer for renderer in [zapi.queryMultiAdapter((paragraph, self, self.request), IParagraphRenderer) for paragraph in self.context.getVisibleParagraphs(self.request)]
                                                if renderer is not None]
        [renderer.update() for renderer in self.renderers]
