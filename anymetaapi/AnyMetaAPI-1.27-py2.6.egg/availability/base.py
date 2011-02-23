# -*- test-case-name: anymeta.availability.test_service -*-
#
# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

"""
Application availability abstraction.
"""

from twisted.application import service

from zope.interface import implements
from fizzjik import event, interfaces


# the different availability levels that are known.
OK      = 0
NOTICE  = 1
WARNING = 2
ERROR   = 3


class AvailabilityChangedEvent(event.Event):
    """
    A generic event which is thrown when the availability of the
    system has changed. In the "data" field of the event, the
    component is given which was responsible for the change.
    """
    pass



class AvailabilityService (service.MultiService):
    """
    A service which manages several availability components which each
    contribute to the general availability of the system.
    """
    
    implements(interfaces.IController)

    components = None
    event_mappings = None
    widgets = None
    components_by_name = None


    def __init__(self):
        service.MultiService.__init__(self)
        
        self.components = []
        self.event_mappings = []
        self.widgets = []
        self.components_by_name = {}


    def getState(self):
        """
        Return list (component name, state) tuples in which state is
        one of OK, NOTICE, WARNING, ERROR
        """
        return [(c.name, c.getState()) for c in self.components]


    def getPercentage(self):
        """
        Returns the availability of the system, measured as a
        percentage. 100% = fully functional, 0% = completely broken.
        """
        if not len(self.components):
            return 100.
        
        total = ERROR * len(self.components)
        av    = total - sum([x[1] for x in self.getState()])
        return 100 * av/float(total)


    def getStateFull(self):
        """
        Returns a dictionary with full state information per
        component. For each component it returns a dict with: state,
        caption, message, solution.
        """

        result = []
        for c in self.components:
            r = dict(state = c.getState())
            r['caption'] = c.caption
            r['message'], r['solution'] = c.getHelp()
            r['component'] = c
            result.append((c.name, r))
        return result

    
    def addComponent(self, component):
        """
        Add a L{AvailabilityComponent} to the monitoring service.
        """
        self.components.append(component)
        self.components_by_name[component.name] = component
        component.setParent(self)

    def registerObservers(self, hub):
        """
        Implementation function for L{fizzjik.interfaces.IController}:
        registers all events from the controllers and sets up the
        dispatcher functions in the hub.
        """
        for evt, cb in self.event_mappings:
            hub.addObserver(evt, cb)
        pass


    def addEvent(self, evt, cb):
        """
        Internal function, called by the L{AvailabilityComponent}s to setup event handlers.
        """
        self.event_mappings.append((evt, cb))


    def observe(self, event):
        """
        Convenience function which passes "observe" through to parent (which is supposed to be a L{fizzjik.Hub})
        """
        self.parent.observe(event)


    def availabilityChanged(self, component):
        """
        Called by any of the components when the availability
        changed. This fires an L{AvailabilityChangedEvent}.
        """
        self.parent.observe(AvailabilityChangedEvent(component))
        for w in self.widgets:
            w.refresh()

    def __getitem__(self, k):
        """
        Retrieve the component
        """
        return self.components_by_name[k]
            

class AvailabilityComponent:
    """
    A component which is part of the system availability.
    """
    
    # general name for the component, e.g., 'power', 'internet'. Lowercase, no spaces.
    name  = None

    # caption of this component
    caption = "Genereric availability component"

    # the parent (an AvailabilityService); set by AvailabilityService.add_component
    parent = None

    def __init__(self, **kw):
        if 'name' in kw:
            self.name = kw['name']


    def setParent(self, p):
        """
        Set parent. This is the place where to hook up events and
        start services for the component.
        """
        self.parent = p

    def getState(self):
        """
        Return one of OK, NOTICE, WARNING, ERROR
        """
        raise Exception("Implement me")

    def getHelp(self):
        """
        Return a tuple with 2 text: error message, possible
        solution. If there is no solution, a None value should be
        returned instead of a message.
        """
        raise Exception("Implement me")




if __name__ == "__builtin__":

    from fizzjik import hub
    from twisted.application import service

    application = service.Application("test")

    hub = hub.Hub()

    hub.setServiceParent(application)

    # Create service and add some components which we wanna check
    s = AvailabilityService()

    import component
    s.add_component(component.PowerComponent())
    s.add_component(component.InternetComponent())
    
    s.setServiceParent(hub)

    import dbus.mainloop.glib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
