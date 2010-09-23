### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with list of rubric

$Id: rubriccloud.py 52881 2009-04-07 21:09:24Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52881 $"


from rubriclist import RubricList
from pd.lib.linear_quantizator import quantizator, round, elastic
from zope.app.zapi import getUtility
from ng.app.link.linkbackreference.interfaces import ILinkBackReference, ILinkBackReferenceContainer
from zope.app.intid.interfaces import IIntIds
from ng.lib.viewletbase import ViewletBase
from ng.content.article.interfaces import IDocKind
from ng.adapter.ianytitle.interfaces import IAnyTitle

class RubricCloudBase(object) :
    @property
    def values(self) :
        return (x for x,y in self._values)

    @property
    def records(self) :
        return ( {'value':x, 'class':str(y)} for x,y in self._values)

    @property
    def _values(self) :
        rubrics = list(super(RubricCloudBase,self).values)
        if len(rubrics) == 0 :
            raise ValueError
        if len(rubrics) == 1 :
            return ((rubrics[0],3),)
        elif self.request.form.has_key("round") :
            cloud = round([ (x,len(x)) for x in rubrics  ],6)
        else :
            cloud = elastic(quantizator([ (x,len(x)) for x in rubrics ],7),7)

        if 'print' in self.request.form :
            print "============================="
            for rubric,size in sorted(cloud,lambda x,y : cmp(x[1],y[1]) or cmp(len(x[0]),len(y[0])) ) :
                print rubric.title,len(rubric),size
                
            print "============================="

        if self.request.form.has_key("sorted") :
            return reversed(sorted(cloud,lambda x,y : cmp(x[1],y[1]) or cmp(len(x[0]),len(y[0]))))

        return sorted(cloud,lambda x,y : cmp(IAnyTitle(x[0]).title,IAnyTitle(y[0]).title ))
                            
class RubricCloud(RubricCloudBase,RubricList) :
    """ Cloud of rubric for this object
    """

class RubricAllCloudBase(object) :
    @property
    def values(self) :
        brf = getUtility(ILinkBackReference,context=self.context)
        intid = getUtility(IIntIds, brf.newsRefId)
        s = set()
        for items in ILinkBackReferenceContainer(brf) .values() :
            for item in items :
                rubric = intid.getObject(int(item[1:])).__parent__
                rid = intid.getId(rubric)
                if rid not in s :
                    s.update([rid])
                    if not IDocKind(rubric).ishidden :
                        yield rubric


class RubricAllCloud(RubricCloudBase,RubricAllCloudBase,ViewletBase) :
    """ Cloud of all rubric for this object """