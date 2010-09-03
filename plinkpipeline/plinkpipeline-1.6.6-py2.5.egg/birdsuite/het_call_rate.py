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
"""usage: %prog [options]

Produce a report with a line for each sample, with the columns:
sample-name,  call rate for that sample,  (# of het calls)/(total calls) for that sample.
"""

from __future__ import division
import optparse
import sys

import call_confidence_parser

lstRequiredOptions=["callsPath",
                    "confidencesPath",
                    "thresholdFloat",
                    "outputPath"]

def iterateHetCallRate(strCallsPath, strConfidencesPath, fThreshold):
    """For each iteration, returns (Sample, Call Rate, Het Call Rate)"""
    callsParser = call_confidence_parser.CallsConfidencesParser(strCallsPath, strConfidencesPath, fThreshold)

    lstNumCalls = [0] * len(callsParser.lstCELFiles)
    lstNumHetCalls = [0] * len(callsParser.lstCELFiles)

    iNumSNPs = 0
    for strSNP, lstCalls in callsParser.iterateSNPs():
        iNumSNPs += 1
        for i in xrange(len(lstCalls)):
            if lstCalls[i] is not None:
                lstNumCalls[i] += 1

                if lstCalls[i] == "1":
                    lstNumHetCalls[i] += 1

    for i in xrange(len(callsParser.lstCELFiles)):
        yield (callsParser.lstCELFiles[i], lstNumCalls[i]/iNumSNPs, lstNumHetCalls[i]/lstNumCalls[i])
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--calls", dest="callsPath",
                      help="tab-delimited file with 1 line for each SNP, 1 column for each genotype call, plus 1st column is SNP name.  Header line has CEL file name for each column of genotypes.  Genotypes are: 0=AA, 1=AB, 2=BB.")
    parser.add_option("--confidences", dest="confidencesPath",
                      help="tab-delimited file identical to calls file, except that each value in the matrix is a confidence of the "+
                      "corresponding genotype call in the calls file.")
    parser.add_option("--threshold", dest="thresholdFloat", type="float",
                      help="If a genotype has confidence <= this value, it is considered a no-call")
    parser.add_option("-o", "--output", dest="outputPath", help="Where to write the report.  Default: stdout")

    parser.set_defaults(outputPath="-")

    dctOptions, lstArgs = parser.parse_args(argv)

    for strOpt in lstRequiredOptions:
        if getattr(dctOptions, strOpt) is None:
            print >> sys.stderr, 'ERROR:', strOpt, 'argument is required.'
            parser.print_help()
            return 1


    if dctOptions.outputPath == "-":
        fOut = sys.stdout
    else:
        fOut = open(dctOptions.outputPath, "w")

    print >>fOut, "#Sample\tCallRate\tHetCallRate"

    for tupValues in iterateHetCallRate(dctOptions.callsPath, dctOptions.confidencesPath, dctOptions.thresholdFloat):
        print >>fOut, "%s\t%f\t%f" % tupValues

    if dctOptions.outputPath != "-":
        fOut.close()

    return 0
    

if __name__ == '__main__':
    sys.exit(main())
    
