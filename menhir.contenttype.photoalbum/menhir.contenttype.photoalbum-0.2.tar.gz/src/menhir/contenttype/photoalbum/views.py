# -*- coding: utf-8 -*-

import grokcore.component as grok

from dolmen import menu
from dolmen.app.layout import Page
from dolmen.app.viewselector import SelectableViewsMenu
from menhir.contenttype import image, photoalbum
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from menhir.contenttype.photoalbum import MCPMessageFactory as _


def images_iterator(container, url_compute):
    for image in container.values():
        url = url_compute(image)
        yield {'href': url + '/++thumbnail++image.preview',
               'thumb': url + '/++thumbnail++image.square',
               'alt': image.title,
               'title': image.title}
    

@menu.menuentry(SelectableViewsMenu)
class Animated(Page):
    grok.name('gallery_view')
    grok.title(_('label_animatedgallery', default=u"Animated gallery"))
    grok.context(photoalbum.IPhotoAlbum)

    def update(self):
        self.has_images = bool(len(self.context))
        if self.has_images:
            self.baseurl = str(self.request.URL)
            self.contents = images_iterator(self.context, self.url)
            photoalbum.animated_gallery.need()


@menu.menuentry(SelectableViewsMenu)
class Simple(Page):
    grok.name('thumbnails_view')
    grok.title(_('label_simplegallery', default=u"Simple gallery"))
    grok.context(photoalbum.IPhotoAlbum)

    def update(self):
        self.has_images = bool(len(self.context))
        if self.has_images:
            image.ImagePopup.need()
            photoalbum.gallery_css.need()
            self.contents = images_iterator(self.context, self.url)
            self.uid = getUtility(IIntIds).queryId(self.context)
