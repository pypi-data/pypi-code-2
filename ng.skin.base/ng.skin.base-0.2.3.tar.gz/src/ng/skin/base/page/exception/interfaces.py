### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of exceptiion

$Id: interfaces.py 51755 2008-09-20 23:38:41Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.interface import Interface
from zope.schema import URI

class IRedirectException(Interface) :
    """ Basic Skin """

    url = URI(title=u"Redirect url")    