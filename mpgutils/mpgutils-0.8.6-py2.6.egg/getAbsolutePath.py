#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2006 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage: %prog <path>

Creates an absolute path from a relative path.
"""

from __future__ import division
import optparse
import sys
from os.path import abspath

def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    parser = optparse.OptionParser(usage=__doc__)
    dctOptions, lstArgs = parser.parse_args(argv)
    
    if len(lstArgs) !=2:
        print >> sys.stderr, "ERROR: Must have exactly 1 argument.\n"
        parser.print_help()
        return 1
    
    strPath=lstArgs[1]
    strAbsPath=abspath(strPath)
    print (strAbsPath)
    
if __name__ == "__main__":
    sys.exit(main())