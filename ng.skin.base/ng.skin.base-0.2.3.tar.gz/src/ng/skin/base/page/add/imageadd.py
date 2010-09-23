### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for add form to redirect on @@commonedit.html

$Id: imageadd.py 51543 2008-08-29 11:01:24Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from nexturl import NextUrl
from zope.app.file.browser.image import ImageAdd 

class ImageAdd(ImageAdd,NextUrl) :
    """ Content """

