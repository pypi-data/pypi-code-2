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
"""usage %prog [options]

Create an output file that maps each probe to the CNV it resides in.  Probes that are not in a CNV are not written."""

from __future__ import division
import optparse
import sys

import cnv_definition_collection
from mpgutils import utils

lstRequiredOptions = ["cnv_defs", "probe_locus"]

def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-o", "--output",
                      help="""Where to write output.  Default: stdout""")
    parser.add_option("-c", "--cnv_defs",
                      help="""(Required)  CNV definitions file.  Must be relative to same genome build as probe_locus file.""")
    parser.add_option("--probe_locus",
                      help="""(Required)  List of SNP and CN probe locations.
Must be relative to same genome build as cnv_defs file.""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    cnvDefs = cnv_definition_collection.CNVDefinitionCollection(dctOptions.cnv_defs)
    dctProbeLocus = utils.loadProbeLocus(dctOptions.probe_locus)

    if dctOptions.output is None:
        fOut = sys.stdout
    else: fOut = open(dctOptions.output, "w")

    for lstFields in utils.iterateWhitespaceDelimitedFile(dctOptions.probe_locus, iNumFieldsExpected=3):
        strSNP = lstFields[0]
        strChr = utils.convertChromosomeStr(lstFields[1])
        iPosn = int(lstFields[2])
        stCNVs = cnvDefs.getCNVsForLocus(strChr, iPosn)
        for cnv in stCNVs:
            print >> fOut, cnv.strCNVName, strSNP

    if dctOptions.output is not None:
        fOut.close()
    
    


if __name__ == "__main__":
    sys.exit(main())
    
