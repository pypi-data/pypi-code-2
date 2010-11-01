from zope import interface, component
from zope.location.interfaces import ISite
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.traverser.stackinfo.consumer import BaseConsumer
from z3c.traverser.stackinfo import interfaces

class KeyValueConsumer(BaseConsumer):
    interface.implements(interfaces.ITraversalStackConsumer)
    component.adapts(ISite, IBrowserRequest)
    arguments=('key', 'value')
    
