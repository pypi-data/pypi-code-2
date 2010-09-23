### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Main view adapter class

$Id: main.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.publisher.browser import BrowserView    
from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager

def getMain(context,request) :
    return getSiteManager(context=context) \
            .getUtility(IContainer, 'Main')

