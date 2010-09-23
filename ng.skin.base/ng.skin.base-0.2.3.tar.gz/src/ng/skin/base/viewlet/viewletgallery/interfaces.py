### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 54288 2010-09-23 07:20:49Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 54288 $"

from zope.interface import Interface

class IGalleryBoxProvider(Interface):
    """ Interface for GalleryBox provider """
