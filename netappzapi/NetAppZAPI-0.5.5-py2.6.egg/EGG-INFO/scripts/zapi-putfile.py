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
usage = 'zapi-putfile.py <localfile> <device> </vol/path>'
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
    if reactor.running:
        reactor.stop()

def all_ok(ignored):
    if reactor.running:
        reactor.stop()

def do_put_file(options, localfile, device, filepath=None):
    """
    Copy a local file to a NetApp filer
    """
    # open the local file to read data from
    try:
        fd = open( localfile, "r" )
        data = fd.read()
    except Exception, e:
        return defer.fail( e )

    if filepath is None:
        filepath = os.path.basename(localfile)
        pass

    # Fetch the remote file
    d = ztool.put_file(device, filepath, data,
                       username=options.username,
                       password=options.password,
                       scheme=options.scheme,
                       )
    #d.addCallback(got_data, fd)
    return d

def got_data(result, fd):
    zapiresult, data = result
    fd.write(data)
    fd.close()
    
def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    if len(args) == 2:
        d = do_put_file(options, args[0], args[1])
    elif len(args) > 2:
        d = do_put_file(options, args[0], args[1], args[2])
        pass
    d.addCallback(all_ok)
    d.addErrback(all_failed)
    
reactor.callWhenRunning(go, args, options)
reactor.run()
# Exit with an error code, if one was set
sys.exit(outerr)
