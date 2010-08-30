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
from zope.app.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound

# import local interfaces
from interfaces import IDefaultView, ISectionAddFormMenuTarget, ITopicAddFormMenuTarget
from interfaces.container import IContainerBaseView, IActionsColumn, IContainerTableViewActionsCell
from interfaces.skin import IEditFormButtons, ISectionIndexView
from site import ISiteManagerTreeView
from ztfy.blog.interfaces import ISkinnable
from ztfy.blog.interfaces.section import ISection, ISectionInfo, ISectionContainer
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from zope.app import zapi
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements

# import local packages
from container import OrderedContainerBaseView
from skin import BaseAddForm, BaseEditForm, BasePresentationEditForm, BaseIndexView, SkinSelectWidgetFactory
from ztfy.blog.section import Section
from ztfy.skin.menu import MenuItem
from ztfy.utils.unicode import translateString

from ztfy.blog import _


class SectionContainerContentsViewMenu(MenuItem):
    """Sections container contents menu"""

    title = _("Sections")


class SectionAddFormMenu(MenuItem):
    """Sections container add form menu"""

    title = _(" :: Add section...")


class SectionTreeViewDefaultViewAdapter(object):

    adapts(ISection, IZTFYBlogBackLayer, ISiteManagerTreeView)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@contents.html'

    def getAbsoluteURL(self):
        intids = zapi.getUtility(IIntIds)
        return '++oid++%d/%s' % (intids.register(self.context), self.viewname)


class SectionContainerContentsView(OrderedContainerBaseView):
    """Sections container contents view"""

    implements(ISectionAddFormMenuTarget, ITopicAddFormMenuTarget)

    legend = _("Container's sections")
    cssClasses = { 'table': 'orderable' }


class SectionContainerContentsViewCellActions(object):

    adapts(ISectionContainer, IZTFYBlogLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        container = ISectionContainer(self.context)
        if not (container.sections or container.topics):
            klass = "ui-workflow ui-icon ui-icon-trash"
            intids = zapi.getUtility(IIntIds)
            return '''<span class="%s" title="%s" onclick="$.ZBlog.container.remove(%s,this);"></span>''' % (klass,
                                                                                                             translate(_("Delete section"), context=self.request),
                                                                                                             intids.register(self.context))
        return ''


class SectionAddForm(BaseAddForm):

    implements(ISectionAddFormMenuTarget)

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new section")

    fields = field.Fields(ISectionInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    def updateWidgets(self):
        super(SectionAddForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    def create(self, data):
        section = Section()
        section.shortname = data.get('shortname', {})
        return section

    def add(self, section):
        language = II18n(self.context).getDefaultLanguage()
        name = translateString(section.shortname.get(language), forceLower=True, spaces='-')
        ids = list(self.context.keys()) + [name, ]
        self.context[name] = section
        self.context.updateOrder(ids)

    def nextURL(self):
        return '%s/@@contents.html' % zapi.absoluteURL(self.context, self.request)


class SectionEditForm(BaseEditForm):

    legend = _("Section properties")

    fields = field.Fields(ISectionInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    buttons = button.Buttons(IEditFormButtons)

    def updateWidgets(self):
        super(SectionEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(SectionEditForm, self).handleApply(self, action)

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZBlog.form.reset(this.form);'


class SectionPresentationEditForm(BasePresentationEditForm):
    """Section presentation edit form"""

    legend = _("Edit section presentation properties")

    parent_interface = ISection


class BaseSectionIndexView(BaseIndexView):
    """Base section index view"""

    implements(ISectionIndexView)

    def update(self):
        if not self.context.visible:
            raise NotFound(self.context, 'index.html', self.request)
        super(BaseSectionIndexView, self).update()
        self.topics = self.context.getVisibleTopics()
