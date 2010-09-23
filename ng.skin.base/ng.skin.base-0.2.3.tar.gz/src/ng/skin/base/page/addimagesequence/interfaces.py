### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.app.photo package

$Id: interfaces.py 52438 2009-01-31 21:51:08Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52438 $"

from zope.interface import Interface
from zope.schema import TextLine, Text, Tuple, Object, Bytes, Bool
from zope.app.file.interfaces import IImage

class IPhotoItem(Interface) :
    title = TextLine(
        title = u'Title',
        description = u'Title',
        default = u'',
        missing_value=u'',
        required = False)

    abstract = Text(
        title = u'Abstract',
        description = u'Some photo description',
        default = u'',
        missing_value=u'',
        required = False
        )

    data = Bytes(
        title=u'Data',
        description=u'The actual content of the object.',
        default='',
        missing_value='',
        required=False,
        )

class IPhotoSequence(Interface) :
    ishidden = Bool(
        title = u"Hidden", 
        default=False, 
        required=True)    

    photos = Tuple(
        min_length=20,
        max_length=20,
        title=u'Photos',
        description=u'Photos',
        value_type=Object(
            title=u'Photo description',
            schema=IPhotoItem))


