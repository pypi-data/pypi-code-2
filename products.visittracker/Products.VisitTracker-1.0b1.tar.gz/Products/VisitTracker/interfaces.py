from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable

class IVisitable(IAttributeAnnotatable):
    """ interface for visitable objects
    """
    
    revisit = interface.Attribute(
        """integer: the time delta (hours) a revisit is tracked as new visit""")
    
class IVisitTracker(interface.Interface):
    """ Adapter to track visits
    """
    
    def getVisits():
        """ get list of visits
        """
    
    def getLastVisit(userid=None):
        """ get the last visit (absolute or by user)
        """
        
    def getLastVisits():
        """ get list of last visits by user
        """
    
    def getNumberOfVisits(userid=None):
        """ gets the number of visits (absolute or by user)
        """
        
    def trackVisit():
        """ track a visit
        """
