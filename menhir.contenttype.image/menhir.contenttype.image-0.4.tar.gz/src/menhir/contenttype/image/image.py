# -*- coding: utf-8 -*-

import dolmen.content as content

from dolmen.file import ImageField
from dolmen.blob import BlobProperty
from dolmen.app.content import icon, IDescriptiveSchema
from dolmen.app.security.content import CanAddContent
from menhir.contenttype.image import MF as _


class IImage(IDescriptiveSchema):
    """Defines a simple object that contains an image.
    """
    image = ImageField(
        title=_(u"Image"),
        required=True)


class Image(content.Content):
    """A simple image storing its data in a blob.
    """
    icon("image.png")
    content.name(_(u"Image"))
    content.schema(IImage)
    content.require(CanAddContent)

    image = BlobProperty(IImage['image'])
