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
"""%prog [-c exclusionfile -o outputfile] <allele_summary>

Read the locus summary file as produced by cn_locus_summarize, as well as the probeset exclusion file produced
by cn_create_exclude_list.  Enhance the exclusion list to exclude individual/probes that have a signal of <=0 
and write those results out as a new file.
"""
from __future__ import division
import optparse
import sys
import numpy

iPROBESET_ID_FIELD = 0
iFIRST_INTENSITY_FIELD = 1

    
def loadExclusionsFile(exclusionFile):
    """Load up the exclusions file, return a dictionary where the key is the 
    probeset name, and the value is the set of excluded individual indexes for that probe."""
    
    fIn = open(exclusionFile)
    dctExclusions={}
    for strLine in fIn:
        lstFields=strLine.split()
        if (lstFields[0]!="probeset_id"):
            strProbeset=lstFields[0]
            lstExcludedIndex=lstFields[1].split(",")
            dctExclusions[strProbeset]=set (lstExcludedIndex)
    return dctExclusions

def addNegativeIntensityExclusions(strMissingValueLabel, dctExclusions, alleleSummaryFile):
    """Modifies the exclusions dictionary to have any intensity sample/probe that is less than 0."""
    print ("Excluding sample/probes with missing value of " + strMissingValueLabel)
    fIn = open(alleleSummaryFile)
    strLine = None
    iCounter=0
    for strLine in fIn:
        if not (strLine.startswith("#") or strLine.startswith("probeset_id")):
            lstFields = strLine.split()
            strProbeSet=lstFields[iPROBESET_ID_FIELD]
            #cut off the -A or -B
            strProbeSet=strProbeSet[:-2]
            intensity=lstFields[iFIRST_INTENSITY_FIELD:]  
            
            #logging progress of file reading.
            if iCounter%10000==0: print ".",
            iCounter=iCounter+1
            
            for i in range(0,len(intensity)):
                ci=intensity[i]
                if ci==strMissingValueLabel:
                    #index is 0 based, exclusion output is 1 based.
                    exclusionIndex=i +1
                    if strProbeSet in dctExclusions:
                        dctExclusions[strProbeSet].add(str(exclusionIndex))
                    else:
                        newExclusions=set()
                        newExclusions.add(str(exclusionIndex))
                        dctExclusions[strProbeSet]=newExclusions
    print
    return dctExclusions

def writeExclusions(dctExclusions, outFile):
    "Write the exclusions dictonary out in the proper exclusions format."
    fOut = open(outFile, "w")
    header=['probeset_id','exclude_list']
    print >>fOut, "\t".join(header)
    
    for strProbeName in dctExclusions.keys():
        stExcludeSampleIndices=dctExclusions[strProbeName]
        lstExcludSampleIndices=[int (iIndex) for iIndex in stExcludeSampleIndices]
        lstExcludSampleIndices.sort()
        print >>fOut, strProbeName + "\t" + ",".join([str(iIndex) for iIndex in lstExcludSampleIndices])
        
    fOut.close()
    
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", dest="output",
                      help="""Where to write output.  Default: stdout""")

    parser.add_option("-c", "--birdseed-exclusions", dest="birdseed_exclusions",
                      help="""The birdseed exclusions file.""")
    
    parser.add_option("-m", "--missing_value_label", dest="missingValueLabel", default="NaN", 
                      help="""Label of data that is missing from the platform.  
                      Illumina products do not always have data available for every probe/individual combination.
                      Default is %default""")
    
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) == 1:
        print >> sys.stderr, "ERROR: allele summary file not specified.\n"
        parser.print_help()
        return 1

    if len(lstArgs) > 2:
        print >> sys.stderr, "ERROR: Too many files on command line.\n"
        parser.print_help()
        return 1

    alleleSummaryFile=lstArgs[1]
    outFile=dctOptions.output
    strMissingValueLabel=dctOptions.missingValueLabel
    
    if dctOptions.output is None:
        print >> sys.stderr, "ERROR: Must define an output file name.\n"
        parser.print_help()
        return 1
    if dctOptions.birdseed_exclusions is None:
        print >> sys.stderr, "ERROR: Must define a birdseed_exclusions file name.\n"
        parser.print_help()
        return 1

    dctExclusions=loadExclusionsFile(dctOptions.birdseed_exclusions)
    dctExclusions=addNegativeIntensityExclusions(strMissingValueLabel, dctExclusions, alleleSummaryFile)
    writeExclusions(dctExclusions, outFile)
                
    #write out results.
    print ("FINISHED")

if __name__ == "__main__":
    sys.exit(main())
    
