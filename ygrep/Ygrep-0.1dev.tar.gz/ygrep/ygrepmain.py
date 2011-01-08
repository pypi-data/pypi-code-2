#! /usr/bin/python
import sys
from optparse import OptionParser
from ygreplib import Ygrep

usage = """\
%prog [options] PATTERN 
Search for PATTERN in each YAML FILE or standard input.
PATTERN is a basic regular expression.
Example: %prog -c 'hello world'\
"""
parser = OptionParser(usage=usage)
parser.add_option("-c", "--color", dest="color", action="store_true",
                  help="use markers to highlight the matching strings")
(options, args) = parser.parse_args()
if len(args) < 1:
    parser.error("PATTERN missing")
pattern = args[0]
res = Ygrep(pattern, options.color).do_it(sys.stdin)
if not res: 
    exit(1)
print res
