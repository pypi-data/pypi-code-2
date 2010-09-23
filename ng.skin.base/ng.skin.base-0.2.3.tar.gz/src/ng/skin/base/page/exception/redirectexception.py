### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ErrorView - is base class for zope3 errors

$Id: redirectexception.py 51755 2008-09-20 23:38:41Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49544 $"


from zope.interface import implements
from interfaces import IRedirectException

class RedirectException(Exception) :
    implements(IRedirectException)
    
    url = ""
    
    def __init__(self,url) :
        self.url = url
        