# -*- coding: utf-8 -*-

import grokcore.view as grok
import dolmen.app.layout as layout

from menhir.contenttype.image import IImage, ImagePopup
from zope.size import ISized


class ImageView(layout.Index):
    """Default view for an image.
    """
    grok.context(IImage)

    def update(self):
        ImagePopup.need()
        url = self.url(self.context)
        self.size = ISized(self.context.image).sizeForDisplay()
        self.thumbnail = "%s/++thumbnail++image.preview" % url
        self.popup_url = "%s/++thumbnail++image.large" % url
        self.download_url = "%s/++download++image" % url
