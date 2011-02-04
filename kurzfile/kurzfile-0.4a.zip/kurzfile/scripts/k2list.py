#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# k2list.py
#
"""List all objects in Kurzweil K-series object files.

You can pass multiple KRZ, K25 or K26 files on the command line. With the
standard text output format, each file will be listed under its own filename
heading. For the CSV output format, one big listing with columns for the
filename, filesize and path will be generated.

"""

__revision__    = '$Id: k2list.py 514 2011-02-04 12:26:52Z carndt $'
__usage__       = "%prog [OPTIONS] KRZFILE..."

# standard library modules
import logging
import glob
import optparse
import os
import sys

from os.path import basename, dirname, isdir, isfile, expanduser

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
    optparser.add_option('-g', '--globs',
        dest="wildcards", action="store_true",
        help="Expand shell glob patterns in input filenames (for use "
           "without a proper shell. eg. on Windows).")
    optparser.add_option('-o', '--output',
        dest="output", metavar="FILE",
        help="Write output to FILE instead of standard output.")
    optparser.add_option('--strict',
        action="store_true", dest="strict",
        help="Abort operation when an error occurs parsing a file instead of "
            "continuing with the next. Mainly useful for debugging")
    optparser.add_option('-s', '--sorty-by',
        dest="sortby", metavar="PROPLIST",
        help="Sort list by given object properties. Valid property names are "
            "'id', 'type', 'type_name', 'name' and 'size'. Multiple property "
            "names must be separated by commas.")

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

    if options.sortby:
        options.sortby = [k.strip() for k in options.sortby.split(',')
                         if k.strip()]

    if args:
        if options.output:
            outfile = open(options.output, 'wb')
        else:
            outfile = sys.stdout

        format = 'csv' if options.csv else 'pretty'

        if format == 'csv':
            print >>outfile, \
                "Type;ID;Name;Size;File name;File size;Path"

        errors = {}; parsed = []
        for filename in args:
            basen = basename(filename)

            if isfile(filename):
                try:
                    kurzfile = Kurzfile(filename, strict=options.strict)
                except ParseError as exc:
                    log.error("%s: %s", basen, exc)
                    errors[filename] = str(exc)

                    if options.strict:
                        break
                else:
                    if format == 'pretty':
                        print >>outfile, basen
                        print >>outfile, "=" * len(basen)
                        print >>outfile
                        print >>outfile, "Path: %s" % dirname(filename)
                        print >>outfile, \
                            "File size: %s" % display_size(kurzfile.filesize)
                        print >>outfile, kurzfile.header

                    try:
                        kurzfile.list_objects(outfile, format,
                                              sortby=options.sortby)
                    except Exception as exc:
                        log.error("%s: error parsing object data: %s",
                                  basen, exc)
                        log.debug("Exception information", exc_info=True)
                        errors[filename] = str(exc)

                        if options.strict:
                            break

                    parsed.append(filename)
            else:
                if isdir(filename):
                    msg = "Is a directory: %s" % filename
                    log.error(msg)
                else:
                    msg = "No such file: %s", filename
                    log.error(msg)
                errors[filename] = msg

        if options.output:
            outfile.close()
    else:
        log.error("No input files found.")
        optparser.print_help()
        return 2

    if errors:
        errcnt = len(errors)
        log.warning("There %s %i error%s. Use options -v and --strict to debug.",
            "was" if errcnt == 1 else "were", errcnt,"" if errcnt == 1 else "s")
    else:
        log.debug("Read %i input files.", len(parsed))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
