# -*- coding: utf-8 -*-

from zope.interface import Interface
from Products.ATContentTypes.interface.event import IATEvent

from monet.recurring_event import recurring_eventMessageFactory as _

class IEvent(IATEvent):
    """Monet event content type"""

class IMonetRecurringEventLayer(Interface):
    """Marker interface for monet.recurring_event layer"""
