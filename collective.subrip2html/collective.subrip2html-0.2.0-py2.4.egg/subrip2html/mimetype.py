# -*- coding: utf-8 -*-

from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem

class SubRipMimetype(MimeTypeItem):

    __name__   = "SubRip"
    mimetypes  = ('text/srt', 'application/x-subrip', 'text/plain')
    extensions = ("srt",)
    globs      = ("*.srt",)
    binary     = 0
