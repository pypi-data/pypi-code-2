#!/usr/bin/env python3

import sys
import optparse
from sexpy import compile_file, run_file, toplevel

if __name__ == '__main__':

    if not sys.argv[1:]:
        toplevel()
        sys.exit()

    opt_parser = optparse.OptionParser(usage="%s [-c] FILENAME" % __file__)
    opt_parser.add_option('-c', action='store_true', dest='compile', help='compile file to Python bytecode')
    options, args = opt_parser.parse_args()

    if len(args) != 1:
        opt_parser.print_help()
        sys.exit(1)

    if options.compile:
        compile_file(args[0])
    else:
        run_file(args[0])
