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
import os

# import Zope3 interfaces
from zope.app.intid.interfaces import IIntIds
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView
from ztfy.blog.layer import IZTFYBlogBackLayer
from ztfy.gallery.interfaces import IGalleryImageInfo, IGalleryImage, IGalleryImageExtension, \
                                    IGalleryContainer, IGalleryContainerTarget

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.template.template import getLayoutTemplate, getViewTemplate
from zc import resourcelibrary
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import adapts
from zope.event import notify
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserView, BrowserPage
from zope.schema import TextLine
from zope.traversing import namespace

# import local packages
from ztfy.blog.browser.container import OrderedContainerBaseView
from ztfy.blog.browser.resource import ZipArchiveExtractor, TarArchiveExtractor
from ztfy.blog.browser.skin import BaseDialogAddForm, BaseDialogEditForm
from ztfy.file.schema import ImageField
from ztfy.gallery.gallery import GalleryImage
#from ztfy.gallery.skin.menu import GallerySkinMenuItem, GallerySkinJsMenuItem
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.gallery import _


class GalleryImageDefaultViewAdapter(object):

    adapts(IGalleryImage, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return """javascript:$.ZBlog.dialog.open('%s/%s')""" % (zapi.absoluteURL(self.context, self.request),
                                                                self.viewname)


class GalleryContainerNamespaceTraverser(namespace.view):
    """++gallery++ namespace"""

    def traverse(self, name, ignored):
        result = getParent(self.context, IGalleryContainerTarget)
        if result is not None:
            return IGalleryContainer(result)
        raise TraversalError('++gallery++')


class IGalleryImageAddFormMenuTarget(Interface):
    """Marker interface for gallery images add menu"""


class GalleryContainerContentsViewMenuItem(MenuItem):
    """Gallery container contents menu"""

    title = _("Images gallery")


class IGalleryContainerContentsView(Interface):
    """Marker interface for gallery container contents view"""

class GalleryContainerContentsView(OrderedContainerBaseView):
    """Gallery container contents view"""

    implements(IGalleryImageAddFormMenuTarget, IGalleryContainerContentsView)

    legend = _("Images gallery")
    cssClasses = { 'table': 'orderable' }

    output = ViewPageTemplateFile('templates/gallery_contents.pt')

    def update(self):
        resourcelibrary.need('ztfy.gallery.back')
        resourcelibrary.need('ztfy.jquery.fancybox')
        super(GalleryContainerContentsView, self).update()

    @property
    def values(self):
        return IGalleryContainer(self.context).values()

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
        self.updateOrder(IGalleryContainer(self.context))

    def getImagesExtensions(self, image):
        return sorted((a[1] for a in zapi.getAdapters((image, self.request), IGalleryImageExtension)),
                      key=lambda x: x.weight)


class GalleryContainerAddImageMenuItem(JsMenuItem):
    """Gallery image add menu"""

    title = _(":: Add image...")

    def render(self):
        resourcelibrary.need('ztfy.i18n')
        return super(GalleryContainerAddImageMenuItem, self).render()


class GalleryImageAddForm(BaseDialogAddForm):
    """Gallery image add form"""

    title = _("New image")
    legend = _("Adding new gallery image")

    fields = field.Fields(IGalleryImageInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True

    def create(self, data):
        return GalleryImage()

    def add(self, image):
        data = self.request.form.get('form.widgets.image')
        filename = getattr(data, 'filename', None)
        if filename:
            filename = translateString(filename, escapeSlashes=True, forceLower=False, spaces='-')
            if not image.image_id:
                self._v_image_id = os.path.splitext(filename)[0]
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

    def updateContent(self, object, data):
        super(GalleryImageAddForm, self).updateContent(object, data)
        if not object.image_id:
            object.image_id = getattr(self, '_v_image_id', None)


class GalleryContainerAddImagesFromArchiveMenuItem(JsMenuItem):
    """Resources from archive add menu item"""

    title = _(":: Add images from archive...")

    def render(self):
        resourcelibrary.need('ztfy.i18n')
        return super(GalleryContainerAddImagesFromArchiveMenuItem, self).render()


class IArchiveContentAddInfo(Interface):
    """Schema for images added from archives"""

    credit = TextLine(title=_("Author credit"),
                      description=_("Default author credits and copyright applied to all images"),
                      required=False)

    content = ImageField(title=_("Archive data"),
                         description=_("Archive content's will be extracted as images ; format can be any ZIP, tar.gz or tar.bz2 file"),
                         required=True)


class GalleryContainerImagesFromArchiveAddForm(BaseDialogAddForm):
    """Add a set of images from a single archive"""

    title = _("New images")
    legend = _("Adding new resources from archive file")

    fields = field.Fields(IArchiveContentAddInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True

    def createAndAdd(self, data):
        filename = self.request.form.get('form.widgets.content').filename
        if filename.lower().endswith('.zip'):
            extractor = ZipArchiveExtractor
        else:
            extractor = TarArchiveExtractor
        extractor = extractor(data.get('content'))
        for info in extractor.getMembers():
            content = extractor.extract(info)
            if content:
                name = translateString(extractor.getFilename(info), escapeSlashes=True, forceLower=False, spaces='-')
                image = GalleryImage()
                notify(ObjectCreatedEvent(image))
                self.context[name] = image
                image.credit = data.get('credit')
                image.image = content
                image.image_id = os.path.splitext(name)[0]


class GalleryImagePropertiesExtension(object):
    """Gallery image properties extension"""

    adapts(IGalleryImage, IZTFYBlogBackLayer)
    implements(IGalleryImageExtension)

    title = _("Properties")
    icon = '/++skin++Gallery/@@/ztfy.blog.img/search.png'
    weight = 1

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def url(self):
        return """javascript:$.ZBlog.dialog.open('%s/@@properties.html')""" % zapi.absoluteURL(self.context, self.request)


class GalleryImageTrashExtension(object):
    """Gallery image trash extension"""

    adapts(IGalleryImage, IZTFYBlogBackLayer)
    implements(IGalleryImageExtension)

    title = _("Delete image")
    icon = '/++skin++Gallery/@@/ztfy.gallery.back.img/trash.png'
    weight = 99

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def url(self):
        intids = zapi.getUtility(IIntIds)
        return """javascript:$.ZBlog.gallery.remove(%d, '%s');""" % (intids.register(self.context),
                                                                     zapi.getName(self.context))


class GalleryImageEditForm(BaseDialogEditForm):
    """Gallery image edit form"""

    legend = _("Edit image properties")

    fields = field.Fields(IGalleryImageInfo)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True


class GalleryImageDiapoView(BrowserView):
    """Display gallery image as diapo"""

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        pass

    render = getViewTemplate()


class GalleryImageIndexView(BrowserPage):
    """Gallery image default view"""

    def __call__(self):
        return zapi.queryMultiAdapter((self.context.image, self.request), Interface, 'index.html')()
