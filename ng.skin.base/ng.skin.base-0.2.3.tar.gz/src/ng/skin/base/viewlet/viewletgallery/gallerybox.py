### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with project box

$Id: gallerybox.py 54288 2010-09-23 07:20:49Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 54288 $"

from zope.app.container.interfaces import IContainer
from ng.skin.base.viewlet.viewletmain.mainbox import MainBox

class GalleryBox(MainBox) :
    """ Gallery box
    """
    
    foldername = "gallery"
    folderinterface = IContainer
