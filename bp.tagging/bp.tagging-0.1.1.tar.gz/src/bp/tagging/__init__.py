#!/usr/bin/env python2.6
# encoding: utf-8
"""
__init__.py

Created by disko on 2010-08-29.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import baker
import exceptions
import mutagen
import mutagen.mp3
import os
import sys

from file import File


# CONFIGURATION


# IMPLEMENTATION

@baker.command
def info(filename):
    """display all available metadata information for <filename>"""
    
    try:
        f = File(fname=filename)
    except IOError, e:
        print e
        return None
    
    if f is None:
        print "unsupported filetype - cannot extract metadata"
        return None
    
    f.pprint()
    #print f.mime
    #print f.info
    #print f.tags


def main():
    """main entry point"""
    
    try:
        baker.run()
    except baker.CommandError, e:
        print "\n%s\n" % e
        print "Run '%s -h' for help.\n" % os.path.split(sys.argv[0])[-1]



if __name__ == '__main__':
    baker.run()
