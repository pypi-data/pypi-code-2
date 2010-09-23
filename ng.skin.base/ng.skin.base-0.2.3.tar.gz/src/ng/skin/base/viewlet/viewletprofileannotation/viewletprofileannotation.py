### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for profileannotation viewlet

$Id: viewletprofileannotation.py 52319 2009-01-13 12:34:49Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50943 $"
 
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation 
from ng.lib.viewletbase import ViewletBase

class ProfileAnnotationViewlet(ViewletBase) :
    def __init__(self,*kv,**kw) :
        super(ProfileAnnotationViewlet,self).__init__(*kv,**kw)
        self.parent = self.context
        self.context = IProfileAnnotation(self.context)
