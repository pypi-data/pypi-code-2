#!/usr/bin/python
# -*- coding: utf-8 -*-

import dolmen.content as content

from dolmen.app.content import icon, IDescriptiveSchema
from dolmen.app.security import CanAddContent
from dolmen.app.viewselector import IViewSelector
from menhir.contenttype.image import IImage
from menhir.contenttype.photoalbum import MCPMessageFactory as _
from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.interface import implements


class IPhotoAlbum(IDescriptiveSchema, IContainer):
    """Defines a folder that can only contain IImage providing objects.
    """
    contains(IImage)


class PhotoAlbum(content.OrderedContainer):
    """A folder that contains images.
    """
    icon("resources/album.png")
    content.name(_(u"Photo album"))
    content.require(CanAddContent)
    content.schema(IPhotoAlbum)

    implements(IViewSelector)
    selected_view = u"thumbnails_view"
