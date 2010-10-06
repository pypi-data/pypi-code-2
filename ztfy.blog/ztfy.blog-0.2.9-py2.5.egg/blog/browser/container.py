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
from z3c.formjs import ajax
from z3c.language.switch.interfaces import II18n
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from interfaces import IDefaultView, IContainedDefaultView, IContainerAddFormMenuTarget
from interfaces.container import IContainerBaseView, IOrderedContainerBaseView
from interfaces.container import IIdColumn, INameColumn, IOrderedContainerSorterColumn, ITitleColumn, \
                                 IStatusColumn, IActionsColumn
from interfaces.container import IContainerTableViewTitleCell, IContainerTableViewStatusCell, IContainerTableViewActionsCell
from ztfy.blog.interfaces.container import IOrderedContainer

# import Zope3 packages
from z3c.table.column import Column, FormatterColumn, GetAttrColumn
from z3c.table.table import Table
from zc import resourcelibrary
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements

# import local packages
from skin import BaseTemplateBackView
from ztfy.skin.menu import MenuItem
from ztfy.utils.timezone import tztime

from ztfy.blog import _


class ContainerContentsViewMenu(MenuItem):
    """Container contents menu"""

    title = _("Contents")


class IdColumn(Column):

    implements(IIdColumn)

    weight = 0
    cssClasses = { 'th': 'hidden',
                   'td': 'hidden id' }

    def renderHeadCell(self):
        return u''

    def renderCell(self, item):
        return zapi.getName(item)


class NameColumn(IdColumn):

    implements(INameColumn)

    cssClasses = {}

    def renderCell(self, item):
        result = zapi.getName(item)
        adapter = zapi.queryMultiAdapter((item, self.request, self.table), IContainedDefaultView)
        if adapter is None:
            adapter = zapi.queryMultiAdapter((item, self.request, self.table), IDefaultView)
        if adapter is not None:
            result = '<a href="%s">%s</a>' % (adapter.getAbsoluteURL(), result)
        return result


class OrderedContainerSorterColumn(Column):

    implements(IOrderedContainerSorterColumn)

    header = u''
    weight = 1
    cssClasses = { 'th': 'sorter' }

    def renderCell(self, item):
        return '<img class="handler" src="/++skin++ZBlog.BO/@@/ztfy.blog.img/sort.png" />'


class TitleColumn(Column):

    implements(ITitleColumn)

    header = _("Title")
    weight = 10
    cssClasses = { 'td': 'title' }

    def renderCell(self, item):
        i18n = II18n(item)
        adapter = zapi.queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewTitleCell)
        prefix = (adapter is not None) and adapter.prefix or ''
        before = (adapter is not None) and adapter.before or ''
        after = (adapter is not None) and adapter.after or ''
        suffix = (adapter is not None) and adapter.suffix or ''
        result = "%s%s%s" % (before, i18n.queryAttribute('title', request=self.request) or '{{ ' + zapi.getName(item) + ' }}', after)
        adapter = zapi.queryMultiAdapter((item, self.request, self.table), IContainedDefaultView)
        if adapter is None:
            adapter = zapi.queryMultiAdapter((item, self.request, self.table), IDefaultView)
        if adapter is not None:
            result = '<a href="%s">%s</a>' % (adapter.getAbsoluteURL(), result)
        return '%s%s%s' % (prefix, result, suffix)


class CreatedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Created')
    weight = 100

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'created'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(tztime(value))
        return value


class ModifiedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Modified')
    weight = 110

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'modified'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(tztime(value))
        return value


class StatusColumn(Column):

    implements(IStatusColumn)

    header = _("Status")
    weight = 200
    cssClasses = { 'td': 'status' }

    def renderCell(self, item):
        adapter = zapi.queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewStatusCell)
        if adapter is not None:
            return adapter.content
        return ''


class ActionsColumn(Column):

    implements(IActionsColumn)

    header = _("Actions")
    weight = 210
    cssClasses = { 'td': 'actions' }

    def renderCell(self, item):
        adapter = zapi.queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewActionsCell)
        if adapter is not None:
            return adapter.content
        return ''


class ContainerBaseView(BaseTemplateBackView, Table):
    """Container-like base view"""

    implements(IContainerBaseView)

    def __init__(self, context, request):
        super(ContainerBaseView, self).__init__(context, request)
        Table.__init__(self, context, request)

    def update(self):
        super(ContainerBaseView, self).update()
        Table.update(self)
        resourcelibrary.need('ztfy.jquery.ui.css')
        resourcelibrary.need('ztfy.jquery.jsonrpc')


class OrderedContainerBaseView(ajax.AJAXRequestHandler, ContainerBaseView):

    implements(IOrderedContainerBaseView, IContainerAddFormMenuTarget)

    sortOn = None
    interface = None

    legend = _("Container's content")
    cssClasses = { 'table': 'orderable' }

    output = ViewPageTemplateFile('templates/ordered.pt')

    def update(self):
        super(OrderedContainerBaseView, self).update()
        resourcelibrary.need('ztfy.jquery.ui.base')
        resourcelibrary.need('ztfy.jquery.jsonrpc')

    @ajax.handler
    def ajaxUpdateOrder(self, *args, **kw):
        self.updateOrder()

    def updateOrder(self, context=None):
        ids = self.request.get('ids')
        if context is None:
            context = self.context
        container = IOrderedContainer(context)
        container.updateOrder(ids, self.interface)
