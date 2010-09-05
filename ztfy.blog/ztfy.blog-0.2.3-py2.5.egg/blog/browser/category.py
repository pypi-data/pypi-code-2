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
from z3c.json.interfaces import IJSONWriter
from z3c.language.switch.interfaces import II18n
from zope.app.intid.interfaces import IIntIds
from zope.traversing.interfaces import TraversalError

# import local interfaces
from interfaces import IDefaultView
from interfaces.container import ITitleColumn, IActionsColumn
from interfaces.container import IContainerTableViewTitleCell, IContainerTableViewActionsCell
from interfaces.skin import IDialogAddFormButtons
from ztfy.blog.interfaces.category import ICategory, ICategoryInfo, ICategoryManager, ICategoryManagerTarget, ICategorizedContent
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import ajax, jsaction
from z3c.template.template import getLayoutTemplate
from zc import resourcelibrary
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import adapts
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.traversing import namespace

# import local packages
from container import ContainerBaseView
from skin import BaseDialogAddForm, BaseDialogEditForm
from ztfy.blog.category import Category
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.blog import _


class ICategoryAddFormMenuTarget(Interface):
    """Marker interface for category add menu"""


class CategoryManagerContentsMenuItem(MenuItem):
    """Category manager contents menu"""

    title = _("Categories")


class CategoryManagerAddCategoryMenuItem(JsMenuItem):
    """Category add menu"""

    title = _(":: Add Category...")

    def render(self):
        resourcelibrary.need('ztfy.i18n')
        return super(CategoryManagerAddCategoryMenuItem, self).render()


class CategoryManagerNamespaceTraverser(namespace.view):
    """++category++ namespace"""

    def traverse(self, name, ignored):
        result = ICategoryManager(self.context, None)
        if result is not None:
            return result
        raise TraversalError('++category++')


def getValues(parent, context, output):
    output.append((parent, context))
    for item in context.values():
        getValues(context, item, output)


class ICategoryManagerContentsView(Interface):
    """Marker interface for category manager contents view"""

class CategoryManagerContentsView(ajax.AJAXRequestHandler, ContainerBaseView):
    """Category manager contents view"""

    implements(ICategoryAddFormMenuTarget, ICategoryManagerContentsView)

    legend = _("Topics categories")
    sortOn = None
    cssClasses = { 'table': 'foldertree treeview' }
    output = ViewPageTemplateFile('templates/categories.pt')

    def __init__(self, context, request):
        super(CategoryManagerContentsView, self).__init__(context, request)
        self.intids = zapi.getUtility(IIntIds)

    @property
    def values(self):
        result = []
        for item in ICategory(self.context).values():
            getValues(None, item, result)
        return result

    def renderRow(self, row, cssClass=None):
        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = '%s %s' % (self.cssClassSelected, cssClass)
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        (parent, context), _col, _colspan = row[0]
        if parent is not None:
            cssClass += ' child-of-node-%d' % self.intids.register(parent)
        id = 'id="node-%d"' % self.intids.register(context)
        cssClass = self.getCSSClass('tr', cssClass)
        cells = [self.renderCell(context, col, colspan)
                 for (parent, context), col, colspan in row]
        return u'\n    <tr %s%s>%s\n    </tr>' % (id, cssClass, u''.join(cells))

    def update(self):
        super(CategoryManagerContentsView, self).update()
        resourcelibrary.need('ztfy.jquery.treetable')

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            target = self.intids.getObject(int(oid))
            parent = zapi.getParent(target)
            del parent[zapi.getName(target)]
            return "OK"
        return "NOK"


class CategoryManagerTreeViewTitleColumnCellAdapter(object):

    adapts(ICategory, IZTFYBlogLayer, ICategoryManagerContentsView, ITitleColumn)
    implements(IContainerTableViewTitleCell)

    prefix = u''
    after = u''
    suffix = u''

    def __init__(self, context, request, table, column):
        self.context = context
        self.request = request
        self.table = table
        self.column = column

    @property
    def before(self):
        return '<span class="ui-icon"></span>'


class CategoryManagerTreeViewActionsColumnCellAdapter(object):

    adapts(ICategory, IZTFYBlogLayer, ICategoryManagerContentsView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column
        self.intids = zapi.getUtility(IIntIds)

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-squaresmall-plus"
        result = '''<span class="%s" title="%s" onclick="$.ZBlog.dialog.open('++category++/@@addCategory.html?parent=%d');"></span>''' % (klass,
                                                                                                                                        translate(_("Add sub-category"), context=self.request),
                                                                                                                                        self.intids.register(self.context))
        klass = "ui-workflow ui-icon ui-icon-trash"
        result += '''<span class="%s" title="%s" onclick="$.ZBlog.form.remove(%d, this);"></span>''' % (klass,
                                                                                                            translate(_("Delete (sub-)category"), context=self.request),
                                                                                                            self.intids.register(self.context))
        return result


class CategoryAddForm(BaseDialogAddForm):
    """Category add form"""

    title = _("New category")
    legend = _("Adding new category")

    fields = field.Fields(ICategoryInfo)
    buttons = button.Buttons(IDialogAddFormButtons)

    layout = getLayoutTemplate()

    @jsaction.handler(buttons['add'])
    def add_handler(self, event, selector):
        return '$.ZBlog.form.add(this.form, %s);' % self.request.form.get('parent', 'null')

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZBlog.dialog.close();'

    @ajax.handler
    def ajaxCreate(self):
        writer = zapi.getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            self.update()
            return writer.write({ 'parent': self.request.form.get('parent', 'null'),
                                  'output': self.layout() })
        self.createAndAdd(data)
        view = CategoryManagerContentsView(getParent(self.context, ICategoryManagerTarget), self.request)
        view.update()
        return writer.write({ 'parent': self.request.form.get('parent', 'null'),
                              'output': u"<!-- OK -->\n" + view.output() })

    def create(self, data):
        category = Category()
        category.shortname = data.get('shortname', {})
        return category

    def add(self, category):
        parent = self.request.form.get('parent')
        if parent is None:
            context = ICategory(self.context)
        else:
            intids = zapi.getUtility(IIntIds)
            context = intids.getObject(int(parent))
        language = II18n(context).getDefaultLanguage()
        name = translateString(category.shortname.get(language), forceLower=True, spaces='-')
        context[name] = category


class CategoryDefaultViewAdapter(object):

    adapts(ICategory, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '''javascript:$.ZBlog.dialog.open('%s/%s')''' % (zapi.absoluteURL(self.context, self.request), self.viewname)


class CategoryEditForm(BaseDialogEditForm):
    """Category edit form"""

    legend = _("Edit category properties")

    fields = field.Fields(ICategoryInfo)
    layout = getLayoutTemplate()
    parent_interface = ICategoryManagerTarget
    parent_view = CategoryManagerContentsView


class CategorizedContentEditFormMenuItem(MenuItem):

    title = _("Categories")


class ICategorizedContentEditForm(Interface):
    """Marker interface for catgorized contents edit form"""


class CategorizedContentEditForm(ajax.AJAXRequestHandler, ContainerBaseView):

    implements(ICategorizedContentEditForm)

    legend = _("Topic categories")
    sortOn = None
    cssClasses = { 'table': 'foldertree treeview' }
    output = ViewPageTemplateFile('templates/categories.pt')

    def __init__(self, context, request):
        super(CategorizedContentEditForm, self).__init__(context, request)
        self.intids = zapi.getUtility(IIntIds)

    @property
    def values(self):
        result = []
        target = getParent(self.context, ICategoryManagerTarget)
        while (target is not None) and (not ICategoryManager(target).values()):
            target = getParent(target, ICategoryManagerTarget, False)
        if target is not None:
            for item in ICategoryManager(target).values():
                getValues(None, item, result)
        return result

    def renderRow(self, row, cssClass=None):
        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = '%s %s' % (self.cssClassSelected, cssClass)
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        (parent, context), _col, _colspan = row[0]
        if parent is not None:
            cssClass += ' child-of-node-%d' % self.intids.register(parent)
        id = 'id="node-%d"' % self.intids.register(context)
        cssClass = self.getCSSClass('tr', cssClass)
        cells = [self.renderCell(context, col, colspan)
                 for (parent, context), col, colspan in row]
        return u'\n    <tr %s%s>%s\n    </tr>' % (id, cssClass, u''.join(cells))

    def update(self):
        super(CategorizedContentEditForm, self).update()
        resourcelibrary.need('ztfy.jquery.treetable')
        resourcelibrary.need('ztfy.i18n')

    @ajax.handler
    def ajaxUpdate(self):
        oids = self.request.form.get('category', [])
        ICategorizedContent(self.context).categories = [self.intids.getObject(int(oid)) for oid in oids]
        notify(ObjectModifiedEvent(self.context))
        return "OK"


class CategorizedContentEditFormTitleColumnCellAdapter(object):

    adapts(ICategory, IZTFYBlogLayer, ICategorizedContentEditForm, ITitleColumn)
    implements(IContainerTableViewTitleCell)

    before = u''
    after = u''
    suffix = u''

    def __init__(self, context, request, table, column):
        self.context = context
        self.request = request
        self.table = table
        self.column = column
        self.intids = zapi.getUtility(IIntIds)

    @property
    def prefix(self):
        return '<input type="checkbox" %s name="category:list" value="%s" /> ' % (self.context in ICategorizedContent(self.table.context).categories and 'checked="checked"' or '',
                                                                                  self.intids.register(self.context))
