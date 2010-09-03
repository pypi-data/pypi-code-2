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

"""usage: %prog [options] list of fully qualified directories
When running calc_callrate_stat, a reference calls file is required.  If you have sample names that are different from those listed in the file,
then those samples are not scored.  If you have samples that are not in the reference file that 
have the same genotypes as some sample in the reference, this program will map those duplicate reference genotypes into the file.
"""

import sys

import optparse
import os.path
from mpgutils import utils
import string

def readDuplicateMap (inFile):
    """A duplicate map file has 2 columns - the name of the same as it should occur in the new file, 
    and the sample name to copy genotypes from.  This file is tab or space seperated."""
    
    fIn = open(inFile, 'rU')
    dctDupeMap={}
    for strLine in fIn:
         s= strLine.split()
         dupe=s[0]
         original=s[1]
         dctDupeMap[dupe]=original
    fIn.close()
    return (dctDupeMap)     

def guessDuplicateSamples (inFile, colNum):
    """If you wish, you can define duplicate samples to match the original sample name, but have some additional appender.
    This looks for samples that are close to the original name - the original name is a substring of the new name.  
    This takes any tab or space seperated file, and uses one column of the file 
    to indicate the sample names - useful for pedigree or celMap files.  The column numbers are 1-based."""
    
    fIn = open(inFile, 'rU')
    dctDupeMap={}
    sampleNames=[]
    cn=string.atoi(colNum)-1
    for strLine in fIn:
        
        s= strLine.split()
        if len(s)<cn: 
            raise Exception("Column number selected [" + colNum + "] greater than number of available columns [" + len(s)+1 +"]")
        sampleNames.append(s[cn])

    #guess which samples are duplicates
    
    for i in xrange(len(sampleNames)):    
        for j in range (1, len(sampleNames)):
            s=sampleNames[i]
            dupe=sampleNames[j]
            found=dupe.find(s)
            if found>-1 and len(s)<len(dupe):dctDupeMap[dupe]=s
    
    return (dctDupeMap)    
    
def writeRefCallsFile (dctDupeMap, refCallsFile, outFile):
    fOut=open (outFile, "w")
    fIn = open(refCallsFile, 'rU')
    header=fIn.readline().split()
    newHeader, order=getDataOrderList(dctDupeMap, header)
    print ("Total number of samples: " + str (len(newHeader)-1))
    fOut.write("\t".join(newHeader)+"\n")
    counter=0
    for strLine in fIn:
        if (counter%10000==0): print ".",
        s= strLine.split()
        newLine=[s[0]]
        for o in order:
            if (o==-1): newLine.append("-1") 
            else: newLine.append(s[o])
        fOut.write("\t".join(newLine)+"\n")    
        counter+=1
    fOut.close()
    fIn.close()
    print ""
    

def getDataOrderList (dctDupeMap, header):
    """Based on the header, figure out the order the data will be in from the various columns in the output file.
    return both the header and the ordering of data.  If a sample name in the dctDupeMap is not found in the reference calls, that sample
    will have a -1 instead of a position."""
    order=[]
    dctHeaderPositions={}
    newHeader=header
    lstNewOriginalSamples=[]
    for i in range (1, len(header)): dctHeaderPositions[header[i]]=i
    order.extend(range(1, len(header)))
    for duplicate,sample in dctDupeMap.iteritems():
        #if the original sample wasn't included in the data set, you're going to need this as well!
        if sample not in newHeader:
            newHeader.append(sample)
            order.append(-1)
            lstNewOriginalSamples.append(sample)
            
        newHeader.append(duplicate)
        if (dctHeaderPositions.has_key(sample)):
            pos=dctHeaderPositions[sample]
        else:
            pos=-1
        order.append(pos)
    print "Found " + str (len(lstNewOriginalSamples))+ " original samples that were not in reference"    
    return (newHeader, order)
        
def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    if argv is None:
        argv=sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("--sampleMapFile", default=None, 
                      help="""tab-delimited file with 2 columns: new sample name and sample to copy data from.
                      This is not required, but if not used then a sampleListFile must be used.""")
    
    parser.add_option("--sampleListFile", default=None,
                      help="""A file that has a list of sample names in one of the columns.  
                      Samples that contain entire other sample names are related.  
                      NA203-1 and NA203 are related, and NA203-1 will be added to the reference calls 
                      with the same genotypes as NA203.""")
    
    parser.add_option("--sampleListFileIndex", default=None,
                      help="""What column in the sampleListFile should be used to access the sample names?  
                      Required if sampleListFile option is used.""")
    
    parser.add_option ("--reference-calls", default=None,
                       help="""The file containing the reference calls to alter.""")
                       
    parser.add_option("--output", 
                      help="""The name of the output reference calls file.""")
    
    dctOptions, lstArgs = parser.parse_args(argv)

    lstRequiredOptions=["reference_calls", "output"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    if dctOptions.sampleMapFile is None and dctOptions.sampleListFile is None:
        print ("Must use either --sampleMapFile or --sampleListFile option")
        parser.print_help()
        return 1
    
    if dctOptions.sampleListFile is not None and dctOptions.sampleListFileIndex is None:
        print ("If using sampleListFile option, must use sampleListFileIndex")
        parser.print_help()
        return 1
    
    if dctOptions.sampleMapFile is not None: 
        dctDupeMap=readDuplicateMap(dctOptions.sampleMapFile)
    else:
        dctDupeMap=guessDuplicateSamples(dctOptions.sampleListFile, dctOptions.sampleListFileIndex)
    
    print ("Found " +str (len(dctDupeMap.keys())) + " duplicate samples that will be added to the reference calls.")
    
    writeRefCallsFile(dctDupeMap, dctOptions.reference_calls, dctOptions.output)
    
    print("Finishing enhancing reference calls")

if __name__ == '__main__':
    sys.exit(main())
