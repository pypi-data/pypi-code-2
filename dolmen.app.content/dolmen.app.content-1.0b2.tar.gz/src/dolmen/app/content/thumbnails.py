# -*- coding: utf-8 -*-

import grok

from PIL import Image
from cStringIO import StringIO
from dolmen.file import IImageField
from dolmen.blob import BlobValue
from dolmen.content import IContent
from dolmen.forms.base import IFieldUpdate
from dolmen.thumbnailer import Miniaturizer, IImageMiniaturizer, IThumbnailer


class BlobMiniaturizer(Miniaturizer):
    """Miniaturizer handler for `dolmen.content.IBaseContent` objects.
    It adds a 64*64 scale (square) and stores the thumbnails in blobs.
    """
    grok.context(IContent)

    # We store in blob
    factory = BlobValue

    # We add a new size
    scales = {'large': (700, 700),
              'preview': (400, 400),
              'mini': (250, 250),
              'thumb': (150, 150),
              'small': (128, 128),
              'square': (64, 64),
              }


class SquareThumbnailer(grok.Adapter):
    """A named thumbnailer that will crop images to the given size.
    """
    grok.name('square')
    grok.context(IContent)
    grok.implements(IThumbnailer)

    def scale(self, original, size):
        image = original.copy()

        width, height = image.size

        if width > height:
            delta = width - height
            left = int(delta / 2)
            upper = 0
            right = height + left
            lower = height
        else:
            delta = height - width
            left = 0
            upper = int(delta / 2)
            right = width
            lower = width + upper

        image = image.crop((left, upper, right, lower))
        image.thumbnail(size, Image.ANTIALIAS)
        thumbnailIO = StringIO()
        image.save(thumbnailIO, original.format, quality=90)
        thumbnailIO.seek(0)
        return thumbnailIO


@grok.implementer(IFieldUpdate)
@grok.adapter(IContent, IImageField)
def ThumbnailsGeneration(object, field):
    """Event handler triggering the thumbnail generation
    """
    name = field.__name__
    original = getattr(object, name, None)
    handler = IImageMiniaturizer(object)

    # The image has been deleted if 'original' is None
    if original is None:
        # We delete the thumbnails.
        handler.delete(fieldname=name)
    else:
        # We generate the thumbnails.
        handler.generate(fieldname=name)
