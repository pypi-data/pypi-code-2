# -*- coding: utf-8 -*-

from zope.interface import Interface
from monet.recurring_event.interfaces import IEvent as IRecurringEvent

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from monet.calendar.event import eventMessageFactory as _

class IMonetEvent(IRecurringEvent):
    """Description of the Example Type"""
    
class IMonetCalendar(Interface):
    """Identifies objects on which you can use the calendar feature"""
    
class IMonetEventLayer(Interface):
    """Marker interface for monet.calendar.event layer"""