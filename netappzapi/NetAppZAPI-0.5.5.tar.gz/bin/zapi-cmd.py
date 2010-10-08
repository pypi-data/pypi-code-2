#!/usr/bin/python
#
# Run an arbitrary ZAPI XML command on a filer
#
import sys

from twisted.internet import reactor, defer
from netappzapi.zapi import ZAPITool
from netappzapi.options import BaseOptions

version = '1.0'
usage = 'zapi-cmd.py <device> <xml>'

outerr = 0

optparser = BaseOptions(usage=usage, version=version)
options, args = optparser.parseOptions()

if len(args) < 2:
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
def run_cmd(options, device, command):
    """
    Rename a directory on a device
    """
    result = yield ztool.zapi_request(device, command,
                                      username=options.username,
                                      password=options.password,
                                      scheme=options.scheme,
                                      )

    # check the result is ok
    if result.status == 'failed':
        raise Exception("Command failed: %s" % result)
    else:
        print result

def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    d = run_cmd(options, args[0], args[1])
    d.addCallback(all_ok)
    d.addErrback(all_failed)

reactor.callWhenRunning(go, args, options)
reactor.run()

# Exit with an error code, if one was set
sys.exit(outerr)
