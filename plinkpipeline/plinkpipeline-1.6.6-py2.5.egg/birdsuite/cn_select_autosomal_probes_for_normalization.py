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
"""usage: %prog --cnv-probe-info <cnv-file> --snp-probe-info <snp-file> --num-probes <number>

Randomly select some autosomal probes from the probes specified in the input files.
The probe names are written to stdout.
"""

from __future__ import division
import optparse
import random
import sys

import cn_annotate_allele_summary

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--cnv-probe-info", dest="cnvProbeInfo",
                      help="Input file containing metadata for CNV probes.")
    parser.add_option("--snp-probe-info", dest="snpProbeInfo",
                      help="Input file containing metadata for SNP probe sets.")
    parser.add_option("--num-probes", dest="numProbes", type="int",
                      help="The number of probes to select")
    
    
    dctOptions, lstArgs = parser.parse_args(argv)

    if dctOptions.snpProbeInfo is None or dctOptions.cnvProbeInfo is None or dctOptions.numProbes is None:
        print >> sys.stderr, "ERROR: Arguments --snp-probe-info, --cnv-probe-info and --num-probes must be specified.\n"
        parser.print_help()
        return 1

    dctProbeToGenomicPosition = {}
    cn_annotate_allele_summary.mapCNPs(dctProbeToGenomicPosition, dctOptions.cnvProbeInfo)
    cn_annotate_allele_summary.mapSNPs(dctProbeToGenomicPosition, dctOptions.snpProbeInfo)

    lstAutosomalProbes = [strProbeName for strProbeName, tupLocus in dctProbeToGenomicPosition.iteritems() \
                          if strProbeName.startswith("CN_") and tupLocus[0] not in ['23', '24']]

    lstAutosomalProbes.sort()
    
    for strProbe in random.sample(lstAutosomalProbes, dctOptions.numProbes):
        print strProbe

if __name__ == "__main__":
    sys.exit(main())
    
