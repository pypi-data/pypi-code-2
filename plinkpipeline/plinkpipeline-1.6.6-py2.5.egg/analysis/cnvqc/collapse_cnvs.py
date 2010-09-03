#!/util/bin/python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2006 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage: %prog [options] <input file>

Take a file that has 6 columns:
sample_id
chr
start
end
copy_number
score

Looks for common regions, and creates an output file of those common regions.
"""

import sys
import numpy
import optparse
from mpgutils import utils


CNP_DEF_SAMPLE_ID_FIELD_INDEX =0
CNP_DEF_CHR_FIELD_INDEX = 1
CNP_DEF_START_POSN_FIELD_INDEX=2
CNP_DEF_END_POSN_FIELD_INDEX =3
CNP_DEF_COPY_NUMBER_FIELD_INDEX=4
CNP_DEF_CN_SCORE_FIELD_INDEX=5
NUM_CNP_DEFINITION_FIELDS = 6


dctFunctions={"mean":numpy.mean,
              "median":numpy.median,
              "max":numpy.amax}

def mode (items):
    """I have no idea why this isn't in numpy.  If mode ever shows up (or someone can find it), replace
    this function with numpy's."""
    results = {}
    for item in items: 
        results.setdefault(item, 0)
        results[item] += 1
    
    reversed={}
    for key, value in results.items():
        reversed[value]=key
    largest=max(reversed.keys())
    return (reversed[largest])
    
class RangeCNP(object):
    """Holds the definition of a CNP that is described by start and end loci."""
    def __init__(self, strLine):
        lstFields = strLine.split()
        if len(lstFields) < NUM_CNP_DEFINITION_FIELDS - 1 or \
               len(lstFields) > NUM_CNP_DEFINITION_FIELDS:
            raise Exception("Wrong number of fields (%d).  Expected %d fields." % \
                            (len(lstFields), NUM_CNP_DEFINITION_FIELDS))
            
        self.strSampleID = lstFields[CNP_DEF_SAMPLE_ID_FIELD_INDEX]
        self.iChr = int(utils.convertChromosomeStr(lstFields[CNP_DEF_CHR_FIELD_INDEX]))
        self.iStartPosn = int(lstFields[CNP_DEF_START_POSN_FIELD_INDEX])
        self.iEndPosn = int(lstFields[CNP_DEF_END_POSN_FIELD_INDEX])
        self.iCopyNumber=int(lstFields[CNP_DEF_COPY_NUMBER_FIELD_INDEX])
        self.iCNScore=float (lstFields[CNP_DEF_CN_SCORE_FIELD_INDEX])
        
    def getOutputFields(self):
        return [self.strSampleID, str(self.iChr), str(self.iStartPosn), str(self.iEndPosn), str(self.iCopyNumber), str(self.iCNScore)]

    def __str__(self):
        return str(self.getOutputFields())
    
    def cmpCNPDefinitionsByPosition(a, b):
        """Sorts CNPs by locus.  Primary sort is chromosome, then start posn, then end posn"""
        iCmpChromosome = cmp(a.iChr, b.iChr)
        if iCmpChromosome != 0:
            return iCmpChromosome
        iCmpStartPosn=cmp(a.iStartPosn, b.iStartPosn)
        if iCmpStartPosn !=0:
            return iCmpStartPosn
    
        return cmp(a.iEndPosn, b.iEndPosn)
    
    def isOverlapping(self, other, overlapDistance, overlapPercent):
        inner=min(self.iEndPosn, other.iEndPosn)-max(self.iStartPosn, other.iStartPosn)
        outer=max(self.iEndPosn, other.iEndPosn)-min(self.iStartPosn, other.iStartPosn)
        #bug where the cnvs match exactly in size, the overlapPct would be 0 divided by 0.
        if inner==0: inner=1
        if outer==0: outer=1
        
        thisOverlapPct=float (inner)/float (outer)
        
        if(abs(self.iStartPosn - other.iStartPosn)< overlapDistance 
           and abs(self.iEndPosn - other.iEndPosn)<overlapDistance 
           and thisOverlapPct>overlapPercent 
           and self.iChr == other.iChr):
            return True
        return False
    
    def prettyOut (self):
        return "\t".join(self.getOutputFields())
    

def loadRangeCNPDefinitions(strCnpDefsFile):
    """Reads the CNP definitions from the file, does some validation, sorts by genomic positions,
    and returns a list of RangeCNP objects."""
    
    lstRet = []
    fIn = open(strCnpDefsFile)
    strHeader = fIn.readline()
    lstFields = strHeader.split()
    
    for strLine in fIn:
        lstRet.append(RangeCNP(strLine))

    fIn.close()
    lstRet.sort(cmp=RangeCNP.cmpCNPDefinitionsByPosition)
    return lstRet

def getSampleSize(lstRangeCNPs):
    
    setSampleNames=set()
    for cnp in lstRangeCNPs:
        setSampleNames.add(cnp.strSampleID)
    
    print "Number of unique samples" + str(len(setSampleNames))
    return len(setSampleNames)

def filterByScore(lstRangeCNPs, fScoreThreshold):
    """Filter CNPs by score threshold.  They must have a score >= threshold to be incorperated."""

    lstResult=[]
    for cnp in lstRangeCNPs:
        if cnp.iCNScore >=fScoreThreshold:
            lstResult.append(cnp)
    print "retained " + str (len(lstResult)) + " of " + str(len(lstRangeCNPs))+ " events"
    return lstResult

def testFreq(sampleSize, idxIncluded, frequencyThreshold):
    return (float (len(idxIncluded))/float (sampleSize)) > float(frequencyThreshold)
    
def getEventStart(lstRangeCNPs, index, methodName):
    method=dctFunctions[methodName]
    lstTemp=[]
    for i in index:
        lstTemp.append(lstRangeCNPs[i].iStartPosn)
    return int (method(lstTemp))

def getEventEnd(lstRangeCNPs, index, methodName):
    method=dctFunctions[methodName]
    lstTemp=[]
    for i in index:
        lstTemp.append(lstRangeCNPs[i].iEndPosn)
    return int (method(lstTemp))

def writeMergedCNV(baseCNV, lstRangeCNPs, idxIncluded, outFile):
    outFields=[str (baseCNV.iChr), str (baseCNV.iStartPosn), str (baseCNV.iEndPosn)]
    iCount=0
    lstSamples=[]
    for cnpIdx in idxIncluded:
        cnp=lstRangeCNPs[cnpIdx]
        #outFields.append(cnp.strSampleID)
        lstSamples.append(cnp.strSampleID)
        iCount=iCount+1
    outFields.append(str(iCount))
    outFields.extend(lstSamples)
    print >> outFile, "\t".join(outFields)    
    
def findOverlaps (lstRangeCNPs, sampleSize, overlapDistance, overlapPercent, frequencyThreshold, eventBreakPointSummaryMethod, outFile, verbose=True):
    baseCNV=None
    lastGoodIdx=-1
    index=0
    allGoodCNVIdx=[]
    while(index < len(lstRangeCNPs)):
        if baseCNV is None:
            #start at the position after the last good finding.
            index=lastGoodIdx+1
            #the last good index advances by one so we don't get stuck searching.
            lastGoodIdx=index
            #if you've run out of index, write this result and break.
            if (index+1)>=len(lstRangeCNPs):
                break;

            #set up the base CNV to scan.
            baseCNV=lstRangeCNPs[index]
            idxIncluded=[index]
            index=index+1 # set search ahead.
        
        #next CNV to scan.         
        nextCNV=lstRangeCNPs[index]
        if (verbose):
                print ("BaseCNV " + "\t".join(baseCNV.getOutputFields()))
                print ("NextCNV " + "\t".join(nextCNV.getOutputFields()))
                
        #if overlapping, change the base CNV to reflect the mean of the new event merged in.
        if baseCNV.isOverlapping(nextCNV, overlapDistance, overlapPercent):
            if (verbose): print ("merged")
            idxIncluded.append(index)
            
            baseCNV.iStartPosn=getEventStart(lstRangeCNPs, idxIncluded, eventBreakPointSummaryMethod)
            baseCNV.iEndPosn =getEventEnd(lstRangeCNPs, idxIncluded, eventBreakPointSummaryMethod)
            
            lastGoodIdx=index
        #if you fall out of range, or off the chromosome, stop scanning and write results    
        elif (abs (baseCNV.iStartPosn - nextCNV.iStartPosn))> overlapDistance or baseCNV.iChr!=nextCNV.iChr:
            if (verbose): print ("stop merge")
            #test frequency here.
            freqFlag=testFreq(sampleSize, idxIncluded, frequencyThreshold)
            
            #only include events as good if they pass the frequency flag.
            if freqFlag: 
                allGoodCNVIdx.extend(idxIncluded) 
                writeMergedCNV(baseCNV, lstRangeCNPs, idxIncluded, outFile)            
                if (verbose): print ("Final CNV " + "\t".join(baseCNV.getOutputFields()))
            baseCNV=None 
        else:
            if (verbose): print "not merged"    
        index=index+1
    print ("done finding overlaps")
    outFile.close()
    

def generateMap (eventMapFile, mapOutFile, mapPrefix, iMapNumSampleThreshold):
    fIn = open(eventMapFile, 'r')
    fOut = open (mapOutFile, "w")
    iCount=0;
    header=["cnp_id", "chr", "start", "end"]
    print >> fOut, "\t".join(header) 
    
    for strLine in fIn:
        fields = strLine.split()
        if len(fields)>=4 and int (fields[3]) >= iMapNumSampleThreshold:              
            iCount=iCount+1
            
            label=mapPrefix+str(iCount)
            result=[label, fields[0], fields[1], fields[2]]
            print >> fOut, "\t".join(result)
            #print ("accepted for sample size: " +"\t".join(fields))
        else:
            print ("reject for sample size: " + "\t".join(fields))
            
    fIn.close()
    fOut.close()
            
def main(argv=None):
    if argv is None:
        argv = sys.argv

###########
# DICTIONARY OF NUMPY FUNCTIONS FOR BREAKPOINT RESOLUTION
###########
    dctFunctions["mode"]=mode
        
    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("--score_threshold", dest="scoreThreshold", default=10,
                      help="""Filter the events so that they have a score >= the threshold provided.
                      Default score is 10.""")
    
    parser.add_option("--overlap_distance", dest="overlapDistance", default=100000,
                      help="""the maximum distance between the putative CNP's
start/end site and the test CNV's start/end site, for the test CNV to
be added.  Reasonable values are anywhere between 10kb (10000) and 1Mb (1000000).
Default:100000""")
    
    parser.add_option("--overlap_pct", dest="overlapPercent", default=0.3, 
                      help="""he minimum overlap between the putative CNP and the
test CNV, for the test CNV to be added.  Reasonable values are in the
range of 0.01-0.8.  Default .3""")
    
    parser.add_option("--frequency", dest="frequency", default=0.01,
                      help="""the frequency of the new CNP for it to be "worth" being
called a CNP.  Anywhere from 0.00001 to 0.05 is reasonable.  I should
note this number is actually compared to % of the population with a
CNV call, not allele frequency...so 0.05 really corresponds more to a
2.5% AF  Default .01""")
    
    methodOptions=" ".join(dctFunctions.keys())
    
    parser.add_option("--method", dest="method", default="median",
                      help="""The way breakpoints are averaged.  
                      Options are:""" + methodOptions)
    
    parser.add_option("--output_collapsed", dest="outputCollapsed", default="new_cnps.txt",
                      help="""The collapsed CNV output file.  Default is new_cnps.txt""")
    
    parser.add_option("--generateMap", dest="outputMap",
                      help="""(optional) Generate a CNV map that can be used directly with canary.
                      This option selects the filename of the newly generated map
                      If this option is selected, a threshold of # samples observed for 
                      a CNV before it is part of the map can also be set (map_num_samples)""")
    
    parser.add_option("--mapCNVPrefix", dest="mapPrefix",
                      help="""If --generateMap is called, this is the CNV name prefix to use for naming CNVs.
                      Example: CNV, BE_CNV, QS_CNV, MY_FANCY_CNV.""")
    
    parser.add_option("--map_num_samples", dest="mapNumSampleThreshold", 
                      help="""If --generateMap is selected, this sets the number of samples
                      that must be observed for a CNV to be included in the common map.""")
#    parser.add_option("--output_uncollapsed", dest="outputUncollapsed", default="uncollapsed_cnvs.txt",
#                      help="""All cnvs that didn't get added to a new CNP.  Default is new_cnps.txt""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    if len(lstArgs) < 2:
        print >> sys.stderr, "ERROR: Missing required arguments.  Requires at least 1 cnv events file.\n"
        parser.print_help()
        return 1
    
    if dctOptions.outputMap is not None:
        if dctOptions.mapPrefix is None:
            print >> sys.strerr,"ERROR: If generateMap is selected, a CNV prefix name must be selected.\n"
            parser.print_help()
            return 1
        if dctOptions.mapNumSampleThreshold is None:
            print >> sys.strerr,"ERROR: If generateMap is selected, the map_num_samples parameter must be used.\n"
            parser.print_help()
            return 1
        
    #open file for output
    fOut = open(dctOptions.outputCollapsed, "w")
    
    #parse score threshold.
    try:
        fScoreThreshold=float (dctOptions.scoreThreshold)
    except TypeError:
        print (str (dctOptions.scoreThreshold) + "is not a number!")
    
    lstRangeCNPs=loadRangeCNPDefinitions(lstArgs[1])
    lstRangeCNPs=filterByScore(lstRangeCNPs, fScoreThreshold)
    numSamples=getSampleSize(lstRangeCNPs)
    findOverlaps (lstRangeCNPs, numSamples, dctOptions.overlapDistance, dctOptions.overlapPercent, dctOptions.frequency, dctOptions.method, fOut)
    generateMap (dctOptions.outputCollapsed, dctOptions.outputMap, dctOptions.mapPrefix, int (dctOptions.mapNumSampleThreshold))
    print ("FINISHED.")
    
if __name__ == "__main__":
    sys.exit(main())
