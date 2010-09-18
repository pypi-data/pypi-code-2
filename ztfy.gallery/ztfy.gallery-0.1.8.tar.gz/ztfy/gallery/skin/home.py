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
import random
from persistent import Persistent

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.annotation.interfaces import IAnnotations
from zope.app.file.interfaces import IImage
from zope.app.intid.interfaces import IIntIds
from zope.traversing.interfaces import TraversalError

# import local interfaces
from interfaces import IHomeBackgroundImage, IHomeBackgroundManager, \
                       IHomeBackgroundManagerContentsView, \
                       IHomeBackgroundManagerDetailMenuTarget
from ztfy.blog.browser.interfaces import IDefaultView
from ztfy.blog.browser.interfaces.container import IActionsColumn, IContainerTableViewActionsCell
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.table.column import Column
from z3c.template.template import getLayoutTemplate
from zc import resourcelibrary
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.location import locate
from zope.proxy import ProxyBase, setProxiedObject
from zope.publisher.browser import BrowserPage
from zope.schema.fieldproperty import FieldProperty
from zope.traversing import namespace

# import local packages
from menu import GallerySkinMenuItem, GallerySkinJsMenuItem
from ztfy.blog.browser.container import OrderedContainerBaseView
from ztfy.blog.browser.skin import BaseDialogAddForm, BaseDialogEditForm
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer
from ztfy.blog.ordered import OrderedContainer
from ztfy.file.property import ImageProperty
from ztfy.i18n.property import I18nTextProperty
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.gallery import _


#
# Home background images manager
#

class HomeBackgroundManager(OrderedContainer):
    """Home background images manager"""

    implements(IHomeBackgroundManager)

    def getImage(self):
        images = [i for i in self.values() if i.visible]
        if images:
            return random.choice(images)
        return None


HOME_BACKGROUND_IMAGES_ANNOTATIONS_KEY = 'ztfy.gallery.home.background'

class HomeBackgroundManagerAdapter(ProxyBase):

    adapts(ISiteManager)
    implements(IHomeBackgroundManager)

    def __init__(self, context):
        annotations = IAnnotations(context)
        manager = annotations.get(HOME_BACKGROUND_IMAGES_ANNOTATIONS_KEY)
        if manager is None:
            manager = annotations[HOME_BACKGROUND_IMAGES_ANNOTATIONS_KEY] = HomeBackgroundManager()
            locate(manager, context, '++home++')
        setProxiedObject(self, manager)


class HomeBackgroundManagerNamespaceTraverser(namespace.view):
    """++home++ namespace"""

    def traverse(self, name, ignored):
        site = getParent(self.context, ISiteManager)
        if site is not None:
            manager = IHomeBackgroundManager(site)
            if manager is not None:
                return manager
        raise TraversalError('++home++')


class HomeBackgroundManagerContentsMenuItem(GallerySkinMenuItem):
    """HomeBackgroundManager contents menu item"""

    title = _("Home background images")


class HomeBackgroundManagerContentsView(OrderedContainerBaseView):
    """Home background images manager contents view"""

    implements(IHomeBackgroundManagerContentsView,
               IHomeBackgroundManagerDetailMenuTarget)

    legend = _("Home page background images")

    @property
    def values(self):
        return IHomeBackgroundManager(self.context).values()

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
        adapter = zapi.getAdapter(self.context, IHomeBackgroundManager)
        self.updateOrder(adapter)


class IHomeBackgroundManagerPreviewColumn(Interface):
    """Marker interface for home background images container preview column"""

class HomeBackgroundManagerPreviewColumn(Column):
    """Home background images container preview column"""

    implements(IHomeBackgroundManagerPreviewColumn)

    header = u''
    weight = 5
    cssClasses = { 'th': 'preview',
                   'td': 'preview' }

    def renderCell(self, item):
        image = IImage(item.image, None)
        if image is None:
            return u''
        return '''<img src="%s/++display++64x64" alt="%s" />''' % (zapi.absoluteURL(image, self.request),
                                                                   II18n(image).queryAttribute('title', request=self.request))


class HomeBackgroundManagerContentsViewActionsColumnCellAdapter(object):

    adapts(IHomeBackgroundImage, IZTFYBlogLayer, IHomeBackgroundManagerContentsView, IActionsColumn)
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
                                                                                                       translate(_("Delete image"), context=self.request),
                                                                                                       self.intids.register(self.context))
        return result


#
# Home background images
#

class HomeBackgroundImage(Persistent, Contained):
    """Home background image"""

    implements(IHomeBackgroundImage)

    title = I18nTextProperty(IHomeBackgroundImage['title'])
    image = ImageProperty(IHomeBackgroundImage['image'])
    visible = FieldProperty(IHomeBackgroundImage['visible'])


class HomeBackgroundImageAddMenuItem(GallerySkinJsMenuItem):
    """Home background image add menu item"""

    title = _(":: Add image...")

    def render(self):
        resourcelibrary.need('ztfy.i18n')
        return super(HomeBackgroundImageAddMenuItem, self).render()


class HomeBackgroundImageDefaultViewAdapter(object):
    """Container default view adapter for home background images"""

    adapts(IHomeBackgroundImage, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '''javascript:$.ZBlog.dialog.open('%s/%s')''' % (zapi.absoluteURL(self.context, self.request),
                                                                self.viewname)


class HomeBackgroundImageAddForm(BaseDialogAddForm):
    """Home background image add form"""

    title = _("New home background image")
    legend = _("Adding new background image")

    fields = field.Fields(IHomeBackgroundImage)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
    parent_view = HomeBackgroundManagerContentsView
    handle_upload = True

    def create(self, data):
        return HomeBackgroundImage()

    def add(self, image):
        data = self.request.form.get('form.widgets.image')
        filename = None
        if hasattr(data, 'filename'):
            filename = translateString(data.filename, escapeSlashes=True, forceLower=False, spaces='-')
            if filename in self.context:
                index = 2
                name = '%s-%d' % (filename, index)
                while name in self.context:
                    index += 1
                    name = '%s-%d' % (filename, index)
                filename = name
        if not filename:
            index = 1
            filename = 'image-%d' % index
            while filename in self.context:
                index += 1
                filename = 'image-%d' % index
        self.context[filename] = image


class HomeBackgroundImageEditForm(BaseDialogEditForm):
    """Home background image edit form"""

    legend = _("Edit image properties")

    fields = field.Fields(IHomeBackgroundImage)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
    parent_view = HomeBackgroundManagerContentsView
    handle_upload = True


class HomeBackgroundImageIndexView(BrowserPage):
    """Home background image index view"""

    def __call__(self):
        return zapi.queryMultiAdapter((self.context.image, self.request), Interface, 'index.html')()
