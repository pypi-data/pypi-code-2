#!/usr/bin/python
#
# Get an arbitrary file from a NetApp

import sys
import os

from twisted.internet import reactor, defer
from netappzapi.zapi import ZAPITool
from netappzapi.options import BaseOptions

from lxml import etree

version = '1.0'
usage = 'zapi-getfile.py <device> </vol/path> [<localfile>]'
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
    sys.stderr.write("Error: %s: %s\n" % (failure, failure.value))
    if reactor.running:
        reactor.stop()

def all_ok(ignored):
    if reactor.running:
        reactor.stop()

def do_get_file(options, device, filepath, localfile=None):
    """
    Get a file from a remote NetApp, and save it to localfile
    """
    # open the local file to save data to
    if localfile is None:
        localfile = os.path.basename(filepath)
        pass
    try:
        fd = open( localfile, "w" )
    except Exception, e:
        return defer.fail( e )

    # Fetch the remote file
    d = ztool.get_file(device, filepath,
                       username=options.username,
                       password=options.password,
                       scheme=options.scheme,
                       )
    d.addCallback(got_data, fd)
    return d

def got_data(result, fd):
    zapiresult, data = result
    fd.write(data)
    fd.close()
    
def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    if len(args) > 2:
        d = do_get_file(options, args[0], args[1], args[2])
    else:
        d = do_get_file(options, args[0], args[1])
    d.addCallback(all_ok)
    d.addErrback(all_failed)
    
reactor.callWhenRunning(go, args, options)
reactor.run()
# Exit with an error code, if one was set
sys.exit(outerr)
