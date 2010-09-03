#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2007 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""Usage: make_cn_probe_locus_file.py cn_annotation_file > probe_locus_file

Create a file in probe locus format, i.e. with columns SNP name, chromosome, probe-mid
"""

from __future__ import division
import fileinput
import sys

def main(argv=None):
    if argv is None:
        argv = sys.argv

    fIn = fileinput.FileInput(argv[1:])
    for strLine in fIn:
        if not strLine.startswith('#'):
            break
    assert(strLine.startswith('"Probe Set ID"'))

    for strLine in fIn:
        # Remove double quotes and split into fields
        strLine = strLine.rstrip('"\n')
        strLine = strLine.lstrip('"')
        lstFields = strLine.split('","')

        strProbe = lstFields[0]
        strChr = lstFields[1]
        iStart = int(lstFields[2])
        iEnd = int(lstFields[3])

        print "\t".join([strProbe, strChr, str((iStart+iEnd)//2)])

    fIn.close()

if __name__ == "__main__":
    sys.exit(main())
    
