### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for add form to redirect on @@commonedit.html

$Id: nexturl.py 52411 2009-01-30 11:46:32Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.traversing.browser.absoluteurl import absoluteURL

class NextUrl(object) :
    """ Content """

    def create(self, *args, **kw):
       """Do the actual instantiation."""
       self.ob = self._factory(*args, **kw)
       return self.ob
                   

    def nextURL(self):
        return absoluteURL(self.ob,self.request) + "/@@commonedit.html" 
            
            