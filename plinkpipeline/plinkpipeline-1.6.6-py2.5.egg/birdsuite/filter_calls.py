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
"""%prog [options] [calls file | confidence file]

Filter a calls or confidences file according to a list of SNPs to include or exclude,
and/or a list of samples to include or exclude.
"""
from __future__ import division
import fileinput
import optparse
import sys

def filterCalls(fOut, fIn,
                stExcludeSNPs=None,
                stIncludeSNPs=None,
                stExcludeSamples=None,
                stIncludeSamples=None):
    lstColumnsToInclude = None
    strHeader = fIn.readline()
    lstHeader = strHeader.rstrip().split("\t")

    if stExcludeSamples is not None:
        stAllSamples = set(lstHeader[1:])
        stIncludeSamples = stAllSamples - stExcludeSamples
    
    if stIncludeSamples is not None:
        lstColumnsToInclude = [0]
        for strSample in stIncludeSamples:
            lstColumnsToInclude.append(lstHeader.index(strSample))
        lstColumnsToInclude.sort()
        
    if lstColumnsToInclude is None:
        fOut.write(strHeader)
    else:
        print >> fOut, "\t".join([lstHeader[i] for i in lstColumnsToInclude])

    for strLine in fIn:
        lstFields = strLine.rstrip().split("\t")
        if stIncludeSNPs is not None:
            if lstFields[0] not in stIncludeSNPs:
                continue
        elif stExcludeSNPs is not None:
            if lstFields[0] in stExcludeSNPs:
                continue
        if lstColumnsToInclude is None:
            fOut.write(strLine)
        else:
            print >> fOut, "\t".join([lstFields[i] for i in lstColumnsToInclude])


def loadSet(strSetPath):
    f = open(strSetPath)
    stRet = set()
    for strLine in f:
        stRet.add(strLine.strip())
    f.close()
    
    return stRet

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("--exclude-snps", dest="excludeSNPsPath",
                      help="List of SNPs to be excluded from the output, one per line")
    parser.add_option("--include-snps", dest="includeSNPsPath",
                      help="List of SNPs to be included in the output, one per line")
    parser.add_option("--exclude-samples", dest="excludeSamplesPath",
                      help="List of samples to be excluded from the output, one per line")
    parser.add_option("--include-samples", dest="includeSamplesPath",
                      help="List of samples to be included in the output, one per line")
    parser.add_option("-o", "--output", dest="outputPath",
                      help="Where to write output.  Default: stdout")
    parser.set_defaults(outputPath="-")

    dctOptions, lstArgs = parser.parse_args(argv)

    if not dctOptions.excludeSNPsPath and not dctOptions.includeSNPsPath \
       and not dctOptions.excludeSamplesPath and not dctOptions.includeSamplesPath:
        print >> sys.stderr, "ERROR: Must specify one or more of [--exclude-snps, --include-snps, --exclude-samples, --include-samples].\n"
        parser.print_help()
        return 1

    if dctOptions.excludeSNPsPath and dctOptions.includeSNPsPath:
        print >> sys.stderr, "ERROR: --exclude-snps and --include-snps are mutually exclusive.\n"
        parser.print_help()
        return 1
        
    if dctOptions.excludeSamplesPath and dctOptions.includeSamplesPath:
        print >> sys.stderr, "ERROR: --exclude-samples and --include-samples are mutually exclusive.\n"
        parser.print_help()
        return 1
        
    if len(lstArgs) > 2:
        print >> sys.stderr, "ERROR: More than one input file specified on command line.\n"
        parser.print_help()
        return 1

    stExcludeSNPs = None
    stIncludeSNPs = None
    stExcludeSamples = None
    stIncludeSamples = None

    if dctOptions.excludeSNPsPath:
        stExcludeSNPs = loadSet(dctOptions.excludeSNPsPath)
    if dctOptions.includeSNPsPath:
        stIncludeSNPs = loadSet(dctOptions.includeSNPsPath)
    if dctOptions.excludeSamplesPath:
        stExcludeSamples = loadSet(dctOptions.excludeSamplesPath)
    if dctOptions.includeSamplesPath:
        stIncludeSamples = loadSet(dctOptions.includeSamplesPath)

    if dctOptions.outputPath == "-":
        fOut = sys.stdout
    else:
        fOut = open(dctOptions.outputPath, "w")

    filterCalls(fOut, fileinput.input(lstArgs[1:]),
                stExcludeSNPs=stExcludeSNPs,
                stIncludeSNPs=stIncludeSNPs,
                stExcludeSamples=stExcludeSamples,
                stIncludeSamples=stIncludeSamples)

    if dctOptions.outputPath != "-":
        fOut.close()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
    
