# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory

MCPMessageFactory = MessageFactory('menhir.contenttype.photoalbum')

from menhir.contenttype.photoalbum.album import IPhotoAlbum, PhotoAlbum
from menhir.contenttype.photoalbum.libraries import (
    gallery_css, animated_gallery)

__all__ = ("IPhotoAlbum", "PhotoAlbum", "gallery_css", "animated_gallery")
