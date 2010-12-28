# -*- coding: utf-8 -*-

from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException
from Products.MimetypesRegistry.interfaces import IMimetype
from zope.interface import implements
from types import InstanceType

class SubRipMimetype(MimeTypeItem):

    __name__   = "SubRip"
    mimetypes  = ('text/srt', 'application/x-subrip', 'text/plain')
    extensions = ("srt",)
    globs = ("*.srt",)
    binary     = 0
