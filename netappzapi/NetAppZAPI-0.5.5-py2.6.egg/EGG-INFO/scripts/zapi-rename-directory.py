#!/usr/bin/python
#
# Rename a directory on a NetApp
#
import sys

from twisted.internet import reactor, defer
from netappzapi.zapi import ZAPITool
from netappzapi.options import BaseOptions

version = '1.0'
usage = 'zapi-rename-directory.py <device> </vol/old/path> </vol/new/path>'

outerr = 0

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
def rename_directory(options, device, oldname, newname):
    """
    Rename a directory on a device
    """
    command = "<file-rename-directory><from-path>%s</from-path><to-path>%s</to-path></file-rename-directory>" % (oldname, newname)

    result = yield ztool.zapi_request(device, command,
                                      username=options.username,
                                      password=options.password,
                                      scheme=options.scheme,
                                      )

    # check the result is ok
    if result.status == 'failed':
        raise ValueError("Rename failed: %s" % result)

def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    d = rename_directory(options, args[0], args[1], args[2])
    d.addErrback(all_failed)
    d.addCallback(all_ok)

reactor.callWhenRunning(go, args, options)
reactor.run()

# Exit with an error code, if one was set
sys.exit(outerr)
