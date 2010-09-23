### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: contenticons.py 53291 2009-06-15 00:03:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 53291 $"

from ng.lib.viewletbase import ViewletBase
from ng.content.article.interfaces import IIconContainer

class ContentIcons(ViewletBase) :
    """ Content """

    @property
    def images(self) :
        return reversed(IIconContainer(self.context).values())
