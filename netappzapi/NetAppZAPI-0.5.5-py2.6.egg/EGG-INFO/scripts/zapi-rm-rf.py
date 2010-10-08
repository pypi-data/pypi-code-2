#!/usr/bin/python
#
# Recursively delete an entire directory tree, including all
# the files in it.
# GRR! This doesn't work because file-list-directory doesn't
# include things like symlinks in its listing, and there is no
# <file-delete-symlink/> call, though there is a
# <file-create-symlink/> call. Go figure.
# NetApp: Please make qtree delete available outside debug ONTAP.
# Also: Please write a 'delete' function whenever you write a
# 'create' function. Not all of us do our crosswords in pen.
#

import sys
import os
from optparse import OptionParser
from twisted.internet import reactor, defer
from netappzapi.zapi import ZAPITool
from lxml import etree

version = '1.0'
usage = 'zapi-rm-rf.py <device> </vol/path>'

outerr = 0

optparser = OptionParser(usage=usage, version=version)
options, args = optparser.parse_args()

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

@defer.inlineCallbacks
def do_recursive_delete(device, path):
    """
    Perform a recursive delete of the path.
    """
    #print "Deleting in", path
    listing = yield list_directory(device, path)
    # listing is an Element which should have a bunch of children
    # that are <file-info/> nodes.

    for item in listing:

        print etree.tostring(item, pretty_print=True)
        # ignore '.' and '..' entries
        if item.find('name').text in ['.', '..']:
            print "Found '.' or '..' directory. skipping..."
            continue

        if item.find('file-type').text == 'directory':
            #print "Deleting directory", os.path.join(path, item.find('name').text)
            yield do_recursive_delete( device, os.path.join(path, item.find('name').text) )
            pass

        else:
        #elif item.find('file-type').text == 'file':
            print "Deleting file", os.path.join(path, item.find('name').text)
            yield delete_file( device, os.path.join(path, item.find('name').text) )
            print "Deleted", os.path.join(path, item.find('name').text)
            pass
        pass

    # When we get here, we've deleted everything inside this directory, so now we
    # delete the directory itself.
    print "Deleting directory", path
    yield delete_directory( device, path )
    print "Deleted", path

@defer.inlineCallbacks
def delete_directory(device, path):
    """
    Delete a directory on a device
    """
    command = "<file-delete-directory><path>%s</path></file-delete-directory>" % (path)
    result = yield ztool.zapi_request(device, command)

    # check the result is ok
    if result.status == 'failed':
        raise ValueError("Delete failed: %s" % result)

@defer.inlineCallbacks
def delete_file(device, path):
    """
    Delete a directory on a device
    """
    command = "<file-delete-file><path>%s</path></file-delete-file>" % (path)
    result = yield ztool.zapi_request(device, command)

    # check the result is ok
    if result.status == 'failed':
        raise ValueError("Delete failed: %s" % result)

@defer.inlineCallbacks
def list_directory(device, path):
    """
    Get a directory listing from the path, and return it as a list.
    """
    listing = []
    
    result = yield ztool.zapi_request(device, '<file-list-directory-iter-start><path>%s</path></file-list-directory-iter-start>' % path)
    if result.status == 'failed':
        raise ValueError("<file-list-directory-iter-start/> failed: %s" % result)
    #defer.returnValue(listing)

    print "\n directory listing for %s:\n %s" % (path, result)

    tag = result.results.find('tag').text
    maximum = int(result.results.find('records').text)
    
    # Get all the records
    records = 1
    while records > 0:
        result = yield ztool.zapi_request(device, '<file-list-directory-iter-next><tag>%s</tag><maximum>%s</maximum></file-list-directory-iter-next>' % (tag, maximum))

        if result.status == 'failed':
            print("<file-list-directory-iter-next/> failed: %s" % result)
            pass

        files = result.results.find('files')
        if files is not None:
            listing.extend( files )
            pass
        
        records = int(result.results.find('records').text)
        print "Found %d records" % records
        pass
    
    # stop iterating. Don't wait for it to return.
    ztool.zapi_request(device, '<file-list-directory-iter-stop><tag>%s</tag></file-list-directory-iter-stop>' % tag)

    defer.returnValue( listing )
    pass

def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    d = do_recursive_delete(args[0], args[1])
    d.addErrback(all_failed)
    d.addCallback(all_ok)

# Warn the user that this is a dangerous command
# and wait for positive confirmation that we should proceed.
print " === WARNING ==="
print "This is a dangerous command."
answer = raw_input("Are you sure you want to delete everything in %s on device %s (y/[n])? " % (args[1], args[0]) )
if answer.lower().startswith('y'):
    print "Ok. I hope you know what you're doing..."
    reactor.callWhenRunning(go, args, options)
else:
    sys.exit(0)
    pass

reactor.run()
# Exit with an error code, if one was set
sys.exit(outerr)
