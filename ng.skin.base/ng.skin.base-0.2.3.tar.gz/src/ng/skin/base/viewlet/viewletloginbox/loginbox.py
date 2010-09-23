### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with login box

$Id: loginbox.py 52422 2009-01-31 16:30:27Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52422 $"

from ng.lib.viewletbase import ViewletBase

class LoginBox(ViewletBase) :
    """ Login box
    """
    def check(self) :
        if "zope.Authenticated" in self.request.principal.groups :
            raise ValueError
            