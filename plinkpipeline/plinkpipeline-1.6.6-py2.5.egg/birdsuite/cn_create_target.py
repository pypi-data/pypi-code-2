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
"""%prog [options]

Extract the probeset summarized data for a list of CNPs.  This is useful to create a target
data set for probe selection.
"""
from __future__ import division
import optparse
import sys
from birdsuite import cn_probeset_summarize
from mpgutils import utils
from sets import Set

def extendCNPsOld (lstCNPs, interval):
    """Extend each of the CNPs start and end position by the interval size.
    Performs a sanity check to prevent positions from being lower than 1, 
    but does not have a high end check (so a CNP can hang off the end of a chromsome.
    Extend is smart in that it will not extend a CNP definition into another CNP.
    Added: if a CNV is shorter than a previous CNV, ignore it's definition."""
    if (len(lstCNPs))==0:
        return
    
    lstResults=[]
    
    longestEnd=0
    iChr=-1
    coverage=0
    for cnp in lstCNPs:
        if cnp.iChr!=iChr:
            iChr=cnp.iChr
            longestEnd=0
        #if (cnp.strCNPId=="10011"): 
        #    print ("STOP")

        nStart = cnp.iStartPosn - interval
        nEnd=cnp.iEndPosn + interval
        if nStart < 1: nStart=1
        
        #don't modify the start if the end < longest end, as it will be dropped.  
        #otherwise the start can be > the end.  Not good.
        if nStart <= longestEnd and nEnd >  longestEnd: 
            nStart = longestEnd+1
            
        if (nEnd >  longestEnd):
            longestEnd=nEnd
            
                      
            cnp.iStartPosn = nStart
            cnp.iEndPosn = nEnd
            coverage= coverage + (nEnd-nStart)
            lstResults.append(cnp)
             
#        print (str (cnp.iChr) + " " + str (nStart) + " " + str (nEnd))
    print ("Coverage of genome in bp: " + str (coverage))
    return lstResults

def extendCNPs (lstCNPs, interval):
    """Extend each of the CNPs start and end position by the interval size.
    Performs a sanity check to prevent positions from being lower than 1, 
    but does not have a high end check (so a CNP can hang off the end of a chromsome.)"""
    if (len(lstCNPs))==0:
        return
    
    for cnp in lstCNPs:
        cnp.iStartPosn = cnp.iStartPosn - interval
        cnp.iEndPosn = cnp.iEndPosn + interval
        
    return lstCNPs

def getHeader(fIn):
    """Read header from input, write to output, adjusting column headers appropriately."""
    bStart=False
    for strLine in fIn:
        if strLine.startswith("probeset_id"):
            bStart=True
            lstInHeaders = strLine.split()
            break
    return lstInHeaders

def writeProbes (fOut,lstCNPs,lstRowsPerCNP):
    #keep track of which probes have been written.  Only write once.
    seenProbes = Set()
    
    for i, cnp in enumerate(lstCNPs):
        lstRows = lstRowsPerCNP[i]
        if len(lstRows) == 0:
            continue
        
        for probes in lstRows:
            probeName=probes[0]
            if probeName not in seenProbes:
                print >> fOut, "\t".join([str(f) for f in probes])
                seenProbes.add(probeName)
    fOut.close()
            
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-c", "--cnps", dest="cnpDefsFile",
                      help="""Tab-separated input file with the following columns:
CNP ID, chromosome, start genomic position, end genomic position (inclusive).""")
   
    parser.add_option("-s", "--summary", dest="probeSummariesFile",
                      help="""Tab-separated input file with allele or locus probe summaries,
ordered by genomic position.  Required.""")
    
    parser.add_option("-o", "--output", dest="output",
                      help="""Tab-separated output file in tabular format, with one row for each CNP loci summarized in cnpRangeFile
and one column for each sample in the input probeSummaryFile.  Default: stdout.""")
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
                      help="Enable debugging output")
    
    parser.add_option ("-e", dest="extend", default=0,
                       help="""Extend the CNP definitions by a certain number of base pairs in each direction.""")
    
    parser.add_option ("--split_by_chromosome", action="store_true", dest="split", default=False,
                       help="Split output by chromosome.  Each output file and a suffox of .chr<x>, eg: .chr22")
    
    #parser.add_option("--trimIntensity", dest="trimIntensity", default=True, action="store_true",
    #                  help="""Trim intensity data to 0 scale to reduce data size further.  Defaults to integer values.""")
                      
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) > 1:
        print >> sys.stderr, "ERROR: Too many arguments on command line.\n"
        parser.print_help()
        return 1

    if dctOptions.cnpDefsFile is None or dctOptions.probeSummariesFile is None:
        print >> sys.stderr, "ERROR: Missing required arguments.\n"
        parser.print_help()
        return 1
    
    if dctOptions.cnpDefsFile is not None:
        lstCNPs = cn_probeset_summarize.loadRangeCNPDefinitions(dctOptions.cnpDefsFile)

    stCNPIds = set()
    for cnp in lstCNPs:
        if cnp.strCNPId in stCNPIds:
            raise Exception("CNP ID is duplicated: " + cnp.strCNPId)
        else: stCNPIds.add(cnp.strCNPId)

    lstCNPs = extendCNPs(lstCNPs, int(dctOptions.extend))
    
    lstCNPs.sort(cn_probeset_summarize.cmpCNPDefinitionsByPosition)
  
    fIn = cn_probeset_summarize.InputFileWithPushBack(dctOptions.probeSummariesFile)
    #sloshHeader(fOut, fIn, retainAll=False)
    header=getHeader(fIn)
    
    if dctOptions.output is None:
        fOut = sys.stdout
    elif dctOptions.split is False:
         fOut = open(dctOptions.output, "w")
         print >> fOut, "\t".join(header)
    else:
        fOut=None
            
    lstRowsPerCNP = [[] for cnp in lstCNPs]
    lstForIteration = [(cnp, lstRowsPerCNP[i]) for i, cnp in enumerate(lstCNPs)]
    
    iCurrentChromosome=0
    
    for i, strLine in enumerate(fIn):
        #if strLine.startswith("#"):
        #    continue;
        lstFields = strLine.split()
        
        #t=cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX
        #z=lstFields[cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX]
        
        iChromosome=int(utils.convertChromosomeStr(lstFields[cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX]))
        #change of chromosome
        if dctOptions.split and iCurrentChromosome != iChromosome:
            if fOut is not None: 
                writeProbes (fOut,lstCNPs,lstRowsPerCNP)
                
            iCurrentChromosome=iChromosome
            fOut = open(dctOptions.output+'.chr'+str(iCurrentChromosome), "w")
            print >> fOut, "\t".join(header)
            lstRowsPerCNP = [[] for cnp in lstCNPs]
            lstForIteration = [(cnp, lstRowsPerCNP[i]) for i, cnp in enumerate(lstCNPs)]
        
        
            
        lstFields[cn_probeset_summarize.SUMMARY_POSN_FIELD_INDEX] = int(lstFields[cn_probeset_summarize.SUMMARY_POSN_FIELD_INDEX])
        lstFields[cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX] = iChromosome

        # remove from iteration list CNPs that are known to be earlier in position
        while len(lstForIteration) > 0 and \
              (lstForIteration[0][0].iChr < lstFields[cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX] or \
               (lstForIteration[0][0].iChr == lstFields[cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX] and \
                lstForIteration[0][0].iEndPosn < lstFields[cn_probeset_summarize.SUMMARY_POSN_FIELD_INDEX])):
            del lstForIteration[0]
            
        for cnp, lstRows in lstForIteration:
            if cnp.iChr > lstFields[cn_probeset_summarize.SUMMARY_CHR_FIELD_INDEX]:
               break
            iCmp = cnp.cmpToProbeSet(lstFields)
            if iCmp == 0:
                lstRows.append(lstFields)
        if i % 10000 == 0:
            print i
    
    writeProbes (fOut,lstCNPs,lstRowsPerCNP)
            
    fIn.close()
    print "Done"
    
if __name__ == "__main__":
    sys.exit(main())