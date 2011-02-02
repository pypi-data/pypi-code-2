#!/usr/bin/python
# -*- coding: utf-8 -*-

import dolmen.content as content

from dolmen.app.content import icon
from dolmen.app.viewselector import IViewSelector
from menhir.contenttype.image import IImage
from zope.interface import implements
from zope.container.interfaces import IContainer
from zope.container.constraints import contains
from menhir.contenttype.photoalbum import MCPMessageFactory as _


class IPhotoAlbum(IContainer):
    """Defines a folder that can only contain IImage providing objects.
    """
    contains(IImage)


class PhotoAlbum(content.OrderedContainer):
    """A folder that contains images.
    """
    icon("resources/album.png")
    content.name(_(u"Photo album"))
    content.require("dolmen.content.Add")

    implements(IPhotoAlbum, IViewSelector)
    selected_view = u"thumbnails_view"
