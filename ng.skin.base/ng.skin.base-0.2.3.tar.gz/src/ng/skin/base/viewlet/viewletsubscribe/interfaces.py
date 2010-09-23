### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few special interfaces used to bind viewlet provider
and viewlet content

$Id: interfaces.py 51170 2008-06-25 13:07:33Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51170 $"

from zope.viewlet import interfaces
from zope.interface import Interface

class ISubscribeProvider(Interface) :
    """ Interface of newslistbox provider """

    