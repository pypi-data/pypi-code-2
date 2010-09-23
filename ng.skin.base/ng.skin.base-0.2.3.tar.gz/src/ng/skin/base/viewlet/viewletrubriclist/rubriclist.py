### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with list of rubric

$Id: rubriclist.py 52657 2009-02-27 12:10:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52657 $"


from zope.app.zapi import getUtility
from ng.app.link.linkbackreference.interfaces import ILinkBackReference
from zope.app.intid.interfaces import IIntIds
from ng.lib.viewletbase import ViewletBase
from ng.content.article.interfaces import IDocKind

class RubricList(ViewletBase) :
    """ List of rubric for this object
    """

    @property
    def values(self) :
        brf = getUtility(ILinkBackReference,context=self.context)
        intid = getUtility(IIntIds, brf.newsRefId)
        for item in brf["c%016u" % intid.getId(self.context)] :
            ob = intid.getObject(int(item[1:])).__parent__
            
            if not IDocKind(ob).ishidden :
                yield ob
