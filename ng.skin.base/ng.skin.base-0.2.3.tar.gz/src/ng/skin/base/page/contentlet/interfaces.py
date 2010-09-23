### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of viewlet interface for common content page.

$Id: interfaces.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
