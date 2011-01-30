#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# k2list.py
#
"""List all objects in a Kurzweil K-series object file."""

__revision__    = '$Id: k2list.py 490 2011-01-30 02:54:36Z carndt $'
__usage__       = "%prog [OPTIONS] KRZFILE"

# standard library modules
import logging
import glob
import optparse
import os
import sys

from os.path import basename, isdir, isfile, expanduser

# package specific modules
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
        help="Output list in comma-separated values (CSV) format.")
    optparser.add_option('-o', '--output',
        dest="output", metavar="FILE",
        help="Write output to FILE instead of standard output.")
    optparser.add_option('-g', '--globs',
        dest="wildcards", action="store_true",
        help="Expand shell glob patterns in input filenames (for use " + \
           "without a proper shell. eg. on Windows).")

    if args is not None:
        options, args = optparser.parse_args(args)
    else:
        options, args = optparser.parse_args(sys.argv[1:])

    logging.basicConfig(
        level=logging.DEBUG if options.verbose else logging.INFO,
        format="%(levelname)s: %(message)s")
    log = logging.getLogger("k2list")

    if options.wildcards:
        # if asked to, expand wildcards in filename patterns
        # from command line arguments
        filenames = []
        for pat in args:
            filenames.extend(glob.glob(expanduser(pat)))

        args = filenames

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

            if isfile(filename):
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
                if isdir(filename):
                    print >>sys.stderr, "Is a directory: %s" % filename
                else:
                    print >>sys.stderr, "No such file: %s" % filename

        if options.output:
            outfile.close()
    else:
        print >>sys.stderr, "No input files found."
        optparser.print_help()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
