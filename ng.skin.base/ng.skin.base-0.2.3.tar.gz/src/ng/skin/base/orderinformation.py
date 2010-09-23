### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 54215 2010-09-10 11:49:32Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 54215 $"

from ng.lib.orderinformation import OrderInformation

class ContentOrderInformation(OrderInformation) :
    name = ["abstract", "body", "photo",   "backref",  "contenticons", "reference",  "comment", "content", "facebook", "shareit"]

class ColumnOrderInformation(OrderInformation) :
    name = [ "currentbox", "rubriclist", "rubriccloud", "subscribe", "toolbox", "loginbox", "newslistbox"]
