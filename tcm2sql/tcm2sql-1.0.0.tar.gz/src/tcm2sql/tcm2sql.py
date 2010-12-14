#!/usr/bin/env python

# Copyright (C) 2002-2006 gocept gmbh & co.kg, 06112 Halle(Saale), Germany
# Christian Zagrodnick, cz@gocept.com
# Michael Howitz, mh@gocept.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from SSDReader import SSDReader
import __builtin__
import getopt
import re
import sys


availableRenderers = ('Postgres', )


def usage():
    print """\
Usage: tcm2sql -n <file> -w <file> [other_options]
   -n <file>      new SSD file [required]
   -w <file>      write to file [required]
   -o <file>      old SSD file (enables DIFF)
   -r <renderer>  select renderer [currently only Postgres, which is the default]
   --logtables    enable creation of logging tables
   --no_views     disable creation of views for tables
   -h, --help     this message"""


def main():
    oldState = None
    oldStateFile = None
    newState = None
    newStateFile = None
    outFile = None
    rendererName = None

    # this is for having _real_ top level name bindings
    __builtin__.optCreateLoggingTables = 0
    __builtin__.optCreateViews = 1

    opts, args = getopt.getopt(sys.argv[1:],
        "o:n:r:w:h",
        ["oldstate=", "newsate=", "outfile=",
        "renderer=", "logtables",  "help", "no_views"])

    for o,a in opts:
        if o in ('-o','--oldstate'):
            oldStateFile = a
            continue

        if o in ('-n','--newstate'):
            newStateFile = a
            continue

        if o in ('--outfile','-w'):
            outFile = file(a,"w")
            continue

        if o in ('-r', '--renderer', ):
            rendererName = a
            continue

        if o in ('--logtables', ):
            __builtin__.optCreateLoggingTables = 1
            continue

        if o in ('--no_views', ):
            __builtin__.optCreateViews = 0
            continue

        if o in ('-h', '--help'):
            usage()
            sys.exit()

        else:
            print "Unknown Option %s" % (o,)
            usage()
            sys.exit()


    if oldStateFile is not None:
        oldState = SSDReader(oldStateFile)
        oldState.build(__builtin__.optCreateLoggingTables)

    if newStateFile is None or outFile is None:
        usage()
        sys.exit()
    newState = SSDReader(newStateFile)
    newState.build(__builtin__.optCreateLoggingTables)

    if rendererName is None:
        sys.stderr.write("Note: using RenderPostgres\n")
        rendererName = "Postgres"

    _render_module = __import__('Render%s' % rendererName, globals(), locals(), [])
    Renderer = _render_module.Render
    renderer = Renderer(newState, oldState)
    outFile.write(renderer.generateLayout())


