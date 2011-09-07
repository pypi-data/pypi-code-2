#!/usr/bin/env python

import json
from optparse import OptionParser
import sys

from json_grep import JSONGrep

# -----------------------------------
# Main
# -----------------------------------
def parse_args():
    parser = OptionParser()
    parser.set_usage("jgrep [OPTIONS] [FILE (optional)]")
    parser.add_option('-k', '--key' , dest='keys', action='append',
                      help='List of JSON keys to output, arg for each key')

    options, args = parser.parse_args()
    if not options.keys:
        parser.error('Must specify at least one key regex')
        sys.exit()

    return options, args

if __name__ == '__main__':
    options, args = parse_args()
    json_grep = JSONGrep(options.keys)

    try:
        if len(args) <= 0:
            fd = sys.stdin
        else:
            fd = open(args[0])

        for line in json_grep.jgrep_file(fd):
            sys.stdout.write(line)
            sys.stdout.write("\n")
    finally:
        fd.close()

