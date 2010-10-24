from time import time
from zope.interface import implements
from zope.component import adapts, getMultiAdapter

from zope.annotation.interfaces import IAnnotations

from Products.VisitTracker.interfaces import IVisitable, IVisitTracker

VISITTRACKERKEY = 'visits'

class VisitTracker(object):
    """ Adapter to track visits
    """
    implements(IVisitTracker)
    adapts(IVisitable)

    def __init__(self, context):
        self.context = context
        self.registry = IAnnotations(self.context)
    
    def getVisits(self):
        """ get list of visits
        """
        visits = self.registry.get(VISITTRACKERKEY, [])
        if visits is None:
            return []
        return visits
    
    def getLastVisit(self, userid=None):
        """ get the last visit (absolute or by user)
        """
        lastvisits = self.getLastVisits()
        if not lastvisits:
            return None
        if userid is None:
            return lastvisits[0]
        return dict(lastvisits).get(userid, None)
        
    def getLastVisits(self):
        """ get list of last visits by user
        """
        visits = reversed(self.getVisits())
        lastvisits = []
        for date, userid in visits:
            if not userid in dict(lastvisits).keys():
                lastvisits.append((userid, date))
        return lastvisits
    
    def getNumberOfVisits(self, userid=None):
        """ gets the number of visits (absolute or by user)
        """
        if userid is None:
            return len(self.getVisits())
        return dict(self.getVisits()).values().count(userid)
        
    def trackVisit(self):
        """ track a visit
        """
        portal_state = getMultiAdapter((self.context, self.context.request), name=u"plone_portal_state")
        userid = portal_state.member().getId()
        lastvisit = self.getLastVisit(userid)
        visits = self.getVisits()
        if not lastvisit or lastvisit < time() - 3200 * self.context.revisit:
            visits.append((time(), userid))
        else:
            index = visits.index((lastvisit, userid))
            visits[index] = (time(), userid)
            visits.sort(lambda x, y: cmp(x[0], y[0]))
        self.registry[VISITTRACKERKEY] = visits
