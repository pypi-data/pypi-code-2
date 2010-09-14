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
from hurry.query.interfaces import IQuery
from interfaces import IDefaultView
from interfaces.container import IContainerBaseView
from interfaces.container import IStatusColumn, IActionsColumn
from interfaces.container import IContainerTableViewStatusCell, IContainerTableViewActionsCell
from ztfy.blog.interfaces.link import ILinkContainer, ILinkContainerTarget
from ztfy.blog.interfaces.link import IBaseLinkInfo, IInternalLink, IInternalLinkInfo, IExternalLink, IExternalLinkInfo, ILinkFormatter
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.template.template import getLayoutTemplate
from zc import resourcelibrary
from zope.app import zapi
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing import namespace

# import local packages
from container import OrderedContainerBaseView
from skin import BaseDialogAddForm, BaseDialogEditForm
from ztfy.blog.link import InternalLink, ExternalLink
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.catalog.index import Text
from ztfy.utils.text import textToHTML
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.blog import _


class LinkDefaultViewAdapter(object):

    adapts(IBaseLinkInfo, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '''javascript:$.ZBlog.dialog.open('%s/%s')''' % (zapi.absoluteURL(self.context, self.request), self.viewname)


class LinkContainerNamespaceTraverser(namespace.view):
    """++static++ namespace"""

    def traverse(self, name, ignored):
        result = getParent(self.context, ILinkContainerTarget)
        if result is not None:
            return ILinkContainer(result)
        raise TraversalError('++links++')


class ILinkAddFormMenuTarget(Interface):
    """Marker interface for link add menu"""


class LinkContainerContentsViewMenuItem(MenuItem):
    """Links container contents menu"""

    title = _("Links")


class ILinkContainerContentsView(Interface):
    """Marker interface for links container contents view"""

class LinkContainerContentsView(OrderedContainerBaseView):
    """Links container contents view"""

    implements(ILinkAddFormMenuTarget, ILinkContainerContentsView)

    legend = _("Topic links")
    cssClasses = { 'table': 'orderable' }

    def __init__(self, *args, **kw):
        super(LinkContainerContentsView, self).__init__(*args, **kw)

    @property
    def values(self):
        return ILinkContainer(self.context).values()

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            intids = zapi.getUtility(IIntIds)
            target = intids.getObject(int(oid))
            parent = zapi.getParent(target)
            del parent[zapi.getName(target)]
            return "OK"
        return "NOK"

    @ajax.handler
    def ajaxUpdateOrder(self):
        self.updateOrder(ILinkContainer(self.context))


class LinkContainerTableViewCellStatus(object):

    adapts(IBaseLinkInfo, IZTFYBlogLayer, IContainerBaseView, IStatusColumn)
    implements(IContainerTableViewStatusCell)

    def __init__(self, context, request, view, table):
        self.context = context
        self.request = request
        self.view = view
        self.table = table

    @property
    def content(self):
        info = IInternalLinkInfo(self.context, None)
        if info is not None:
            adapter = zapi.queryMultiAdapter((info.target, self.request, self.view, self.table), IContainerTableViewStatusCell)
            if adapter is not None:
                return adapter.content
        return ''


class LinkContainerContentsViewActionsColumnCellAdapter(object):

    adapts(IBaseLinkInfo, IZTFYBlogLayer, ILinkContainerContentsView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column
        self.intids = zapi.getUtility(IIntIds)

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-trash"
        result = '''<span class="%s" title="%s" onclick="$.ZBlog.form.remove(%d, this);"></span>''' % (klass,
                                                                                                       translate(_("Delete link"), context=self.request),
                                                                                                       self.intids.register(self.context))
        return result


class LinkContainerAddInternalLinkMenuItem(JsMenuItem):
    """Internal link add menu"""

    title = _(":: Add internal link...")

    def render(self):
        resourcelibrary.need('ztfy.i18n')
        return super(LinkContainerAddInternalLinkMenuItem, self).render()


class LinkContainerAddExternalLinkMenuItem(JsMenuItem):
    """External link add menu"""

    title = _(":: Add external link...")

    def render(self):
        resourcelibrary.need('ztfy.i18n')
        return super(LinkContainerAddExternalLinkMenuItem, self).render()


class BaseLinkAddForm(BaseDialogAddForm):
    """Base link add form"""

    layout = getLayoutTemplate()
    parent_interface = ILinkContainerTarget
    parent_view = LinkContainerContentsView

    @ajax.handler
    def ajaxCreate(self):
        return super(BaseLinkAddForm, self).ajaxCreate(self)

    def add(self, link):
        title = II18n(link).queryAttribute('title', request=self.request)
        if not title:
            title = translate(_("Untitled link"), context=self.request)
        name = translateString(title, escapeSlashes=False, forceLower=True, spaces='-')
        self.context[name] = link

    @ajax.handler
    def ajaxSearch(self):
        writer = zapi.getUtility(IJSONWriter)
        title = self.request.form.get('title')
        if not title:
            return writer.write(None)
        query = zapi.getUtility(IQuery)
        intids = zapi.getUtility(IIntIds)
        result = []
        for obj in query.searchResults(Text(('Catalog', 'title'),
                                            { 'query': title + '*',
                                              'ranking': True })):
            result.append({ 'oid': intids.register(obj),
                            'title': II18n(obj).queryAttribute('title') })
        return writer.write(result)


class InternalLinkAddForm(BaseLinkAddForm):
    """Internal link add form"""

    title = _("New internal link")
    legend = _("Adding new internal link")

    fields = field.Fields(IInternalLinkInfo).omit('target')

    def create(self, data):
        result = InternalLink()
        result.title = data.get('title', {})
        return result


class ExternalLinkAddForm(BaseLinkAddForm):
    """External link add form"""

    title = _("New external link")
    legend = _("Adding new external link")

    fields = field.Fields(IExternalLinkInfo)

    def create(self, data):
        result = ExternalLink()
        result.title = data.get('title', {})
        return result


class BaseLinkEditForm(BaseDialogEditForm):
    """Base link edit form"""

    legend = _("Edit link properties")

    layout = getLayoutTemplate()
    parent_interface = ILinkContainerTarget
    parent_view = LinkContainerContentsView

    @ajax.handler
    def ajaxEdit(self):
        return super(BaseLinkEditForm, self).ajaxEdit(self)

    @ajax.handler
    def ajaxSearch(self):
        writer = zapi.getUtility(IJSONWriter)
        title = self.request.form.get('title')
        if not title:
            return writer.write(None)
        query = zapi.getUtility(IQuery)
        intids = zapi.getUtility(IIntIds)
        result = []
        for obj in query.searchResults(Text(('Catalog', 'title'),
                                            { 'query': title + '*',
                                              'ranking': True })):
            result.append({ 'oid': intids.register(obj),
                            'title': II18n(obj).queryAttribute('title') })
        return writer.write(result)


class InternalLinkEditForm(BaseLinkEditForm):
    """Internal link edit form"""

    fields = field.Fields(IInternalLinkInfo).omit('target')


class ExternalLinkEditForm(BaseLinkEditForm):
    """External link edit form"""

    fields = field.Fields(IExternalLinkInfo)


class InternalLinkFormatter(object):
    """Internal link default view"""

    adapts(IInternalLink, IZTFYBlogLayer, Interface)
    implements(ILinkFormatter)

    def __init__(self, link, request, view):
        self.link = link
        self.request = request
        self.view = view

    def render(self):
        target = self.link.target
        adapter = zapi.queryMultiAdapter((self.link, self.request, self.view), IDefaultView)
        if adapter is not None:
            url = adapter.absoluteURL()
        else:
            url = zapi.absoluteURL(target, self.request)
        title = II18n(self.link).queryAttribute('title', request=self.request) or \
                II18n(target).queryAttribute('title', request=self.request)
        desc = II18n(self.link).queryAttribute('description', request=self.request) or \
               II18n(target).queryAttribute('description', request=self.request)
        result = ''
        if self.link.language:
            result += '''<img src="/++skin++ZTFY/@@/ztfy.i18n.img/flags/%s.png" alt="" />''' % self.link.language.replace('-', '_', 1)
        result += '''<a href="%s">%s</a>''' % (url, title)
        if desc:
            result += '''<div class="desc">%s</div>''' % textToHTML(desc, request=self.request)
        return '''<div class="link link-internal">%s</link>''' % result


class ExternalLinkFormatter(object):
    """External link default view"""

    adapts(IExternalLink, IZTFYBlogLayer, Interface)
    implements(ILinkFormatter)

    def __init__(self, link, request, view):
        self.link = link
        self.request = request
        self.view = view

    def render(self):
        title = II18n(self.link).queryAttribute('title', request=self.request)
        desc = II18n(self.link).queryAttribute('description', request=self.request)
        result = ''
        if self.link.language:
            result += '''<img src="/++skin++ZTFY/@@/ztfy.i18n.img/flags/%s.png" alt="" />''' % self.link.language.replace('-', '_', 1)
        result += '''<a href="%s">%s</a>''' % (self.link.url, title)
        if desc:
            result += '''<div class="desc">%s</div>''' % textToHTML(desc, request=self.request)
        return '''<div class="link link-external">%s</link>''' % result
