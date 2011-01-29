#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# k2list.py
#
"""List all objects in a Kurzweil K-series object file."""

__author__      = 'Christopher Arndt'
__license__     = 'MIT license'
__revision__    = '$Id: k2list.py 485 2011-01-29 19:41:22Z carndt $'
__usage__       = "%prog [OPTIONS] KRZFILE"

# standard library modules
import logging
import optparse
import os
import struct
import sys
#import time

from os.path import basename, exists

from kurzfile import *


def main(args=None):
    """Main command line interface."""

    global log

    optparser = optparse.OptionParser(usage=__usage__, description=__doc__)
    optparser.add_option('-v', '--verbose',
        action="store_true", dest="verbose",
        help="Print debugging info to standard error output.")
    optparser.add_option('-c', '--csv',
        action="store_true", dest="csv",
        help="Output list in comma-separated value (CSV) format.")
    optparser.add_option('-o', '--output',
        dest="output", metavar="FILE",
        help="Write output to FILE instead of standard output .")

    if args is not None:
        options, args = optparser.parse_args(args)
    else:
        options, args = optparser.parse_args(sys.argv[1:])

    logging.basicConfig(
        level=logging.DEBUG if options.verbose else logging.INFO,
        format="%(levelname)s: %(message)s")
    log = logging.getLogger("k2list")

    if args:
        if options.output:
            outfile = open(options.output, 'wb')
        else:
            outfile = sys.stdout

        format = 'csv' if options.csv else 'pretty'

        if format == 'csv':
            print >>outfile, \
                "ID;Type;Name;Size;File name;File size;Path"

        for filename in args:
            basen = basename(filename)

            if exists(filename):
                try:
                    kurzfile = Kurzfile(filename)
                except ParseError as exc:
                    log.error("%s: %s", basen, exc)
                else:
                    if format == 'pretty':
                        line = "File: %s" % basen
                        print >>outfile, line
                        print >>outfile, "-" * len(line)
                        print >>outfile, \
                            "Size: %s" % display_size(kurzfile.filesize)
                        print >>outfile, kurzfile.header

                    try:
                        kurzfile.list_objects(outfile, format)
                    except Exception as exc:
                        print >>sys.stderr, "Error parsing objects: %s" % exc
            else:
                print >>sys.stderr, "No such file: %s" % filename

        if options.output:
            outfile.close()
    else:
        optparser.print_help()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
