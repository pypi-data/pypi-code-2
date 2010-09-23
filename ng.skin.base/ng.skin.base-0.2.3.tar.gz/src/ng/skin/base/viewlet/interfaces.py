### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 54288 2010-09-23 07:20:49Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 54288 $"

from zope.viewlet import interfaces
from viewletmain.interfaces import INewsListBoxProvider, \
    ICurrentBoxProvider
from viewletsubscribe.interfaces import ISubscribeProvider
from viewletloginbox.interfaces import ILoginBoxProvider
from viewletrubriclist.interfaces import IRubricListProvider,IRubricCloudProvider,IRubricAllCloudProvider
from viewlettoolbox.interfaces import IToolBoxProvider
from viewletgallery.interfaces import IGalleryBoxProvider

class IColumn(
#    IGalleryBoxProvider,
    IToolBoxProvider,
    INewsListBoxProvider, 
    ICurrentBoxProvider, 
    ISubscribeProvider,
    ILoginBoxProvider, 
    IRubricListProvider,
    IRubricCloudProvider,
    IRubricAllCloudProvider,
    interfaces.IViewletManager) :
    """ Column viewlet provider """

class IAnnotations(interfaces.IViewletManager) :
    """ Annotations viewlet provider """


    