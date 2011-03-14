#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.modeling import getter
from woost.models import File
from woost.extensions.blocks.block import Block


class ImageGalleryBlock(Block):

    instantiable = True
    view_class = "woost.views.ImageGallery"

    members_order = [
        "images",
        "gallery_type",
        "thumbnail_width",
        "thumbnail_height",
        "full_width",
        "full_height"
    ]

    images = schema.Collection(
        items = schema.Reference(type = File),
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        member_group = "content"
    )

    gallery_type = schema.String(
        required = True,
        default = "thumbnails",
        enumeration = ["thumbnails", "slideshow"],
        edit_control = "cocktail.html.RadioSelector",
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
               else translations(
                   "ImageGalleryBlock.gallery_type-%s" % value,
                   language,
                   **kwargs
               )
    )

    thumbnail_width = schema.Integer(
        required = True,
        default = 200
    )

    thumbnail_height = schema.Integer(
        required = True,
        default = 200
    )

    full_width = schema.Integer(
        required = True,
        default = 800
    )

    full_height = schema.Integer(
        required = True,
        default = 700
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.images = self.images
        view.gallery_type = self.gallery_type
        view.thumbnail_width = self.thumbnail_width
        view.thumbnail_height = self.thumbnail_height
        view.full_width = self.full_width
        view.full_height = self.full_height

