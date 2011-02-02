# -*- coding: utf-8 -*-

from fanstatic import Resource, Library
from js.galleriffic import galleriffic


GalleryResources = Library("photoalbum.resources", 'resources')

gallery_css = Resource(
    GalleryResources, "gallery.css")

animated_gallery = Resource(
    GalleryResources, "gallery.js", depends=[galleriffic, gallery_css])
