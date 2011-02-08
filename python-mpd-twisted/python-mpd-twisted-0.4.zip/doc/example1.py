#!/usr/bin/env python

# A simple example how to use the MPDProtocol to gather information
# for non-long-running connections e.g. simple cmdline tools.
# If you need a connection which may last longer and should reconnect
# in case of a problem see MPDFactory in doc/example2.py

from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

# Import the protocol. MPD_HOST and MPD_PORT try to read the appropriate
# environment variables or fallback to the default values.
from mpd import MPD_HOST, MPD_PORT, MPDProtocol

# Called after the connection attempt succeeded. You can use protocol with
# commands described in doc/commands.txt since its just an instance of
# MPDProtocol. Remember that each command returns a Deferred!
def connected(protocol):
    # Called after the protocol processed the data without an error.
    # For a more "synchronous" way of doing this check doc/example3.py
    def mpdStatus(result):
        print 'The server\'s status: %s' % result
        reactor.stop()
    
    # Register a callback to get the actual result. You may consider to add
    # an errback as well to handle failures.
    protocol.status().addCallback(mpdStatus)

# This function gets called in case the connector wasn't able to establish
# a connection. If you wan't to watch for connection problems after you
# have been connected you may override protocol.connectionLost
def couldntConnect(failure):
    print 'Couldn\'t connect: %s' % failure.getErrorMessage()
    reactor.stop()

connector = ClientCreator(reactor, MPDProtocol)

# Create the connection and register our callback with the Deferred.
defer = connector.connectTCP(MPD_HOST, MPD_PORT)
defer.addCallback(connected)
defer.addErrback(couldntConnect)

reactor.run()
