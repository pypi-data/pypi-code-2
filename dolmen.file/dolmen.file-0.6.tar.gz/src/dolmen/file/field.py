# -*- coding: utf-8 -*-

from zope.schema import Field
from zope.interface import implements, Interface


class IFileField(Interface):
    """A field storing binary datas.
    """


class IImageField(IFileField):
    """Marker interface for fields storing images.
    """


class FileField(Field):
    """A field handling a file representation
    """
    implements(IFileField)


class ImageField(FileField):
    """A field handling an image file representation
    """
    implements(IImageField)
