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

Make a tfam (transposed family) file from a reference pedigree file, 
a cel_map file mapping a cel file to a sample name, a list of celFiles
that dictates both the subset of individuals, and the order to create them in.
Optionally, the list of celFiles can be extracted from a calls or confidence file."""

from __future__ import division
import optparse
import sys
from mpgutils import utils
import re, os



def main(argv=None):
    if argv is None:
        argv = sys.argv

    lstRequiredOptions=["familyfile", "plateroot"]
    
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-f", "--familyfile",
                      help="""(Required) PLINK formatted .fam file""")
    parser.add_option("-p", "--plateroot",
                      help="""(Required) Contains folders with larry-bird style files""")
    #OPTIONAL
    parser.add_option("-o", "--outputdir",
                      help ="""Define the directory for output files""")
    parser.add_option("-m", "--celmap",
                      help="Cel Map file")
    parser.add_option("-n", "--outputname", default="Output",
                      help="Define the file name root for the output files")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
        
    #VALIDATE PATHS
    lstOptionsToCheck = ['familyfile', 'plateroot', 'outputdir']
    if dctOptions.celmap:
        lstOptionsToCheck.append("celmap")
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
        
    #CHECK PLATE PATH
    pattern = re.compile('[.]merged[.]diploid', re.IGNORECASE)
    CallsPaths = utils.findFiles(dctOptions.plateroot, pattern)
    
    #REMOVE CEL IDS
    celList = getCelsForCallsFile(CallsPaths[0])
    celList = RemoveCels(celList, dctOptions, "probeset_id")
    
    #DICTIONARIES
    dctPedigree = getPedigree(dctOptions.familyfile)
    dctCelSample = utils.readCelMapFile(dctOptions.celmap)
    
    #BUILD TFAM
    buildTFam (celList, dctCelSample, dctPedigree, dctOptions)
    
def RemoveCels(list, options, skip):
    
    for index in range(len(list)):
        item = list[index] 
        item = utils.stripCelExt(item)
        list[index] = item
    return list

def getCelsForCallsFile(callFile):
    """Parse the calls or confidence file, returning the list of cel names"""
    fIn = open(callFile, 'rU')
    line = fIn.readline()
    s=line.split()
    lstCells=s[1:]
    fIn.close()
    return (lstCells)

def getPedigree (pedigreeFile, sampleColumn=2):
    """Parse a pedigree file, return a dictionary of the sample name keyed to the pedigree line"""
    fIn = open(pedigreeFile, 'rU')
    
    dctSamplePedigree={}
    for strLine in fIn:
        s= strLine.split()
        if not strLine.startswith("FAM_ID"):
            strSampleName=s[sampleColumn-1]
            dctSamplePedigree[strSampleName]=strLine
    fIn.close()
    
    return dctSamplePedigree

def buildTFam (celList, dctCelSample, dctPedigree, dctOptions):
    """Given a cel ordering, a way to look up a cel file as a sample, and a pedigree, construct a tFam file"""
    fOut=open(os.path.join(dctOptions.outputdir, dctOptions.outputname + ".tfam"), "w")
    
    lstPedigreeMiss = []
    lstCelMapMiss = []
    
    for cel_id in celList:
        
        #CONVERT CEL TO IID
        snp_id = cel_id
        if dctOptions.celmap:
            if dctCelSample.has_key(cel_id):
                snp_id=dctCelSample[cel_id]
            else:
                lstCelMapMiss.append(cel_id)
        
        #CHECK AGAINST PEDIGREE
        if dctPedigree.has_key(snp_id):
            pedLine=dctPedigree[snp_id]
        else:
            lstPedigreeMiss.append(snp_id)
            pedLine = ("%s\t%s\t0\t0\t-9\t-9\n") % (snp_id, snp_id)
           
        #WRITE OUTPUT
        if pedLine is not None:
            p=pedLine.split("\t")
            #p=map (string.replace(" ", "0"), p)
            z = [fixEmptySampleEntries(x) for x in p ]
                    
            pedLine2=" ".join(z) 
            fOut.write(pedLine2)
    
    if len(lstCelMapMiss) > 0:
        print "\nThe following CEL IDs were not in the CelMap:"
        for item in lstCelMapMiss:
            print "\t" + item
    if len(lstPedigreeMiss) > 0:
        print "\nThe following IDs were not in the Pedigree File:"
        for item in lstPedigreeMiss:
            print "\t" + item
           
    fOut.close()
    print "\nFinished -- MakeTFam.Py\n"
    
def fixEmptySampleEntries (entry):
    if (len(entry)==0): return ("0") 
    return (entry)

if __name__ == "__main__":
    sys.exit(main())
