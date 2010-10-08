#!/usr/bin/python
#
# Create a snapvault snapshot on a snapvault primary, using ZAPI
#
import sys
from optparse import OptionParser

from twisted.internet import reactor, defer

from netappzapi.zapi import ZAPITool
from netappzapi.options import BaseOptions

version = '1.0'
usage = 'zapi-create-snapvault-snapshot-primary <device> <volname> <schedule>'

outerr = 0

# A global for tracking the completion status
completed_d = None

optparser = BaseOptions(usage=usage, version=version)
options, args = optparser.parseOptions()

if len(args) < 3:
    optparser.error("Not enough arguments.")
    sys.exit(1)

ztool = ZAPITool()

def all_failed(failure):
    global outerr
    outerr = 1
    sys.stderr.write("Error: %s\n" % failure.value)
    reactor.stop()

def all_ok(ignored):
    reactor.stop()

@defer.inlineCallbacks
def take_snapshot(options, device, volname, schedule):
    """
    Take a snapshot on a device, given a particular schedule.
    """
    command = "<snapvault-primary-initiate-snapshot-create><volume-name>%s</volume-name><schedule-name>%s</schedule-name></snapvault-primary-initiate-snapshot-create>" % (volname, schedule)

    #print "taking snapshot..."
    result = yield ztool.zapi_request(device, command,
                                      username=options.username,
                                      password=options.password,
                                      scheme=options.scheme,
                                      )

    # check the result is ok
    if result.status == 'failed':
        raise ValueError("Snap failed: %s" % result)

    yield wait_until_complete(options, device, volname)

def wait_until_complete(options, device, volname, delay=5, d=None):
    """
    Check the snapshot every 10 seconds to see if it has completed yet.
    """
    if d is None:
        d = defer.Deferred()
    reactor.callLater(delay, check_snapshot_status, options, device, volname, d)
    return d

@defer.inlineCallbacks
def check_snapshot_status(options, device, volname, d):
    """
    Fetch the status of a snapshot, and d.callback() if it
    has finished.
    """
    #print "checking snapshot status..."
    command = "<snapvault-primary-snapshot-schedule-status-list-info><volume-name>%s</volume-name></snapvault-primary-snapshot-schedule-status-list-info>" % volname

    result = yield ztool.zapi_request(device, command,
                                      username=options.username,
                                      password=options.password,
                                      scheme=options.scheme,
                                      )

    node = result.results.xpath("snapshot-schedule-status/snapvault-snapshot-schedule-status-info[volume-name = '%s']" % volname)[0]

    status = node.find('status').text
    #print "status:", status

    # If the snapshot is still occurring, check again in a bit
    if status == 'Active':
        wait_until_complete(options, device, volname, d=d)
        pass

    # Snapshot is Idle, which means it's finished
    elif status == 'Idle':
        
        #print "Status is not active. All done."
        d.callback(None)

    else:
        d.errback( ValueError("Snapshot status error: '%s'" % status) )

def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    d = take_snapshot(options, args[0], args[1], args[2])
    d.addCallback(all_ok)
    d.addErrback(all_failed)

reactor.callWhenRunning(go, args, options)
reactor.run()

# Exit with an error code, if one was set
sys.exit(outerr)
