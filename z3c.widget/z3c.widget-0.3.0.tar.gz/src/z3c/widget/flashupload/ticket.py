from zope.traversing.browser.absoluteurl import absoluteURL
import random
from zope.app.cache.ram import RAMCache

ticketCache = RAMCache()

def issueTicket(ident):
    """ issues a timelimit ticket 
    >>> type(issueTicket(object()))== type('')
    True
    """
    ticket = str(random.random())
    ticketCache.set(True, ident, key=dict(ticket=ticket))
    return ticket

def validateTicket(ident,ticket):
    """validates a ticket

    >>> validateTicket(object(),'abc')
    False
    >>> obj = object()
    >>> ticket = issueTicket(obj)
    >>> validateTicket(obj,ticket)
    True
    >>> validateTicket(object(),ticket)
    False
    >>> validateTicket(obj,'another')
    False
    """
    ticket =  ticketCache.query(ident,dict(ticket=ticket))
    return ticket is not None

def invalidateTicket(ident,ticket):

    """invalidates a ticket
    >>> ticket = issueTicket(1)
    >>> validateTicket(1,ticket)
    True
    >>> invalidateTicket(1,ticket)
    >>> validateTicket(1,ticket)
    False
    """
    ticketCache.invalidate(ident,dict(ticket=ticket))


class TicketView(object):

    """A view which returns a ticket for its context"""
    def __call__(self):
        return issueTicket(absoluteURL(self.context,self.request))
    
        
        
