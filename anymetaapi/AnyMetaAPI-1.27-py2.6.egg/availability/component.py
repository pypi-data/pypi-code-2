# -*- test-case-name: anymeta.availability.test_component -*-
#
# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

"""
Implementations of AvailabilityComponents.

This module implements the following components:

1. L{PowerComponent} - Monitors the power connector. It goes into
   WARNING state when the computer is running on batter power, and to
   ERROR when the power is critically low.

2. L{InternetComponent} - Monitors the internet connection using
   C{fizzjik.network}. Goes into ERROR state when the connection is
   down. This severity is configurable ('severity' keyword in
   constructor).

3. L{RFIDReaderComponent} - Monitors (dis)connections of rfid readers
   in the system. Can be configured to require a minimum, maximum or
   specific number of readers, as well as requiring specific reader
   serial numbers.

4. L{AnymetaAPIComponent} - Monitor for a working Anymeta connection.

"""
import os

from twisted.internet import task
from twisted.python import log

import base


class PowerComponent(base.AvailabilityComponent):
    """
    Availability component which monitors the power of the computer.
    """
    
    name    = "power"
    caption = "Power connection"

    powerAvailable = True
    powerLow = False

    def setParent(self, parent):
        base.AvailabilityComponent.setParent(self, parent)
        
        from fizzjik.input import power
        self.parent.addEvent(power.PowerAvailableEvent, self.onPowerAvailable)
        self.parent.addEvent(power.LowPowerEvent, self.onLowPower)

        svc = power.PowerMonitor()
        svc.setServiceParent(self.parent)


    def onPowerAvailable(self, event):
        changed = self.powerAvailable != event.data

        self.powerAvailable = event.data
        if changed:
            self.parent.availabilityChanged(self)

    
    def onLowPower(self, event):
        changed = self.powerLow != event.data
        on_battery = event.data
        self.powerLow = on_battery
        if changed:
            self.parent.availabilityChanged(self)


    def getState(self):
        if self.powerLow:
            return base.ERROR
        if not self.powerAvailable:
            return base.WARNING
        return base.OK

    def getHelp(self):
        if self.powerLow:
            return "The computer is very low on power!", "Try finding an elextricity outlet and connect the computer so it can recharge."
        if not self.powerAvailable:
            return "Running on battery power.", None

        return "Power is connected.", None



class InternetComponent(base.AvailabilityComponent):
    """
    Availability component which monitors for a working connection to
    the internet.
    """
    
    name    = "internet"
    caption = "Internet connection"

    severity = base.ERROR # how bad is it that there is no internet?

    connection_present = None

    def __init__(self, **kwargs):
        base.AvailabilityComponent.__init__(self, **kwargs)

        if 'severity' in kwargs:
            self.severity = kwargs['severity']

        
    def setParent(self, parent):
        base.AvailabilityComponent.setParent(self, parent)
        
        from fizzjik.input import network
        self.parent.addEvent(network.NetworkConnectionPresentEvent, self.onConnectionAdded)
        self.parent.addEvent(network.NetworkConnectionAddedEvent, self.onConnectionAdded)
        self.parent.addEvent(network.NetworkConnectionRemovedEvent, self.onConnectionRemoved)

        svc = network.NetworkConnectionSensor()
        svc.destination = "http://hwdeps.mediamatic.nl/ping.php?host=" + os.uname()[1]
        svc.immediate = True
        svc.setServiceParent(self.parent)


    def onConnectionRemoved(self, e):
        changed = self.connection_present
        self.connection_present = False

        if changed:
            self.parent.availabilityChanged(self)


    def onConnectionAdded(self, e):
        changed = not self.connection_present
        self.connection_present = True

        if changed:
            self.parent.availabilityChanged(self)


    def getState(self):
        if not self.connection_present:
            return self.severity
        return base.OK


    def getHelp(self):
        if not self.connection_present:
            return "There is no internet connection.", "Try to find an ethernet cable and plug it in the ethernet port of the computer. Alternatively, configure the computer to use the wireless network."

        return "Internet is available.", None


class RFIDReaderComponent(base.AvailabilityComponent):
    """
    Component which watches for connected RFID readers.

    Options:
    - Minimum / maximum / specific number of readers
    - List of required serial numbers
    """

    name    = "rfid"
    caption = "RFID readers"

    severity = base.ERROR # how bad is it if conditions are not applied?

    min_readers = None
    max_readers = None
    num_readers = None

    serials = None

    connected_readers = None
    greedy = False

    def __init__(self, **kw):
        if 'min_readers' in kw:
            self.min_readers = kw['min_readers']
        if 'max_readers' in kw:
            self.max_readers = kw['max_readers']
        if 'num_readers' in kw:
            self.num_readers = kw['num_readers']
        if 'serials' in kw:
            self.serials = kw['serials']
        if 'greedy' in kw:
            self.greedy = kw['greedy']

        self.connected_readers = []

    
    def setParent(self, parent):
        base.AvailabilityComponent.setParent(self, parent)
        
        from fizzjik.input import sonmicro
        self.parent.addEvent(sonmicro.SonMicroMifareSensorAddedEvent, self.readerAdded)
        self.parent.addEvent(sonmicro.SonMicroMifareSensorRemovedEvent, self.readerRemoved)

        svc = sonmicro.SonMicroMifareSensorMonitor(greedy = self.greedy)
        svc.setServiceParent(self.parent)


    def readerAdded(self, e):
        serial = e.data.serial
        if serial in self.connected_readers:
            return
        self.connected_readers.append(serial)
        self.parent.availabilityChanged(self)
            

    def readerRemoved(self, e):
        serial = e.data
        if serial not in self.connected_readers:
            return
        self.connected_readers.remove(serial)
        self.parent.availabilityChanged(self)


    def getState(self):
        if not self.serials:
            # Not checking on specific serial numbers; check min,max and num.
            if self.min_readers is not None and len(self.connected_readers) < self.min_readers:
                return self.severity
            if self.max_readers is not None and len(self.connected_readers) > self.max_readers:
                return self.severity
            if self.num_readers is not None and len(self.connected_readers) != self.num_readers:
                return self.severity

            return base.OK
        
        else:
            # check for some specific readers.
            if set(self.connected_readers) != set(self.serials):
                return self.severity

            return base.OK


    def getHelp(self):
        if not self.serials:
            # Not checking on specific serial numbers; check min,max and num.
            if self.min_readers is not None and len(self.connected_readers) < self.min_readers:
                return "There need to be at least %d reader(s) connected." % self.min_readers, "Connect at least %d more reader(s)." % (self.min_readers - len(self.connected_readers))
            
            if self.max_readers is not None and len(self.connected_readers) > self.max_readers:
                return "There need to be at maximum %d reader(s) connected." % self.min_readers, "Disconnect %d more reader(s)." % (self.max_readers - len(self.connected_readers))

            if self.num_readers is not None and len(self.connected_readers) != self.num_readers:
                return "There need to be precisely %d reader(s) connected." % self.num_readers, "Please connect the right number of readers."

            return "Readers are configured.", None

        else:
            con  = set(self.connected_readers)
            need = set(self.serials)

            if con != need:
                return "You need to connect specifically the following reader(s): %s" % (", ".join(self.serials)), None
        
            return "Readers are configured.", None


class AnymetaAPIComponent(base.AvailabilityComponent):
    """
    Checks whether the Anymeta API can be reached using a given
    C{AnyMetaAPI} instance and whether it does not return an erroneous
    result.
    """

    name    = "anymeta"
    caption = "Anymeta connection"
    
    # the API to use
    api  = None
    call = "anymeta.user.info"
    call_args = None
    
    # LoopingCall
    lc = None
    state = None
    info = None
    
    severity = base.ERROR
    
    def __init__(self, **kw):
        base.AvailabilityComponent.__init__(self, **kw)
        
        if "api" in kw:
            self.api = kw['api']
            
        if "call" in kw:
            self.call = kw['call']
        if "call_args" in kw:
            self.call_args = kw['call_args']
        else:
            self.call_args = {}

        self.state = self.severity
        

    def setAPI(self, api):
        if api == self.api:
            return

        self.state = self.severity
        self.api = api
        self.info = None
        
        if self.lc and self.lc.running:
            self.lc.stop()
        self._checkStart()

        
    def setParent(self, parent):
        base.AvailabilityComponent.setParent(self, parent)
        self._checkStart()


    def _checkStart(self):
        if not self.api:
            return
        if self.lc and self.lc.running:
            self.lc.stop()

        self.lc = task.LoopingCall(self._checkAnymeta)
        self.lc.start(30)


    def _checkAnymeta(self):
        def connected(result):
            changed = self.state != base.OK
            self.state = base.OK
            self.info = result
            if changed:
                self.parent.availabilityChanged(self)
            
        def not_connected(failure):
            log.err(failure)
            self.result = None
            changed = self.state != self.severity
            self.state = self.severity
            if changed:
                self.parent.availabilityChanged(self)
            
        self.api.doMethod(self.call, self.call_args).addCallback(connected).addErrback(not_connected)


    def getState(self):
        if not self.api:
            return base.NOTICE

        return self.state


    def getHelp(self):
        if not self.api:
            return "No Anymeta connection has been configured.", "Choose an AnyMeta site to connect to."
        if self.state != base.OK:
            return "Anymeta connection failed.", None
        return "Anymeta ok.", None
