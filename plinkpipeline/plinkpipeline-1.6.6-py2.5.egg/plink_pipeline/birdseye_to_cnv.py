#!/usr/bin/env python
import optparse
from mpgutils import utils
import sys
import os
import re

dctCelFileMap = {}
dctFamMap = {}
dctFamMissing = {}

def main(argv = None): 
    if not argv:
        argv = sys.argv
       
    #OPTION PARSING!
    lstRequiredOptions=["familyfile", "plateroot"]
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-p", "--plateroot",
                      help="""(Required) Contains folders with larry-bird style files""")
    parser.add_option("-f", "--familyfile",
                      help="""(Required) PLINK formatted .fam file""")
    parser.add_option("-d", "--outputdir",
                      help ="""(Required) Define the directory for output files""")
    #OPTIONAL
    parser.add_option("-m", "--celmap",help="Cel Map file")
    parser.add_option("-n", "--outputname", default="Output",
                      help="Define the file name root for the output files")
    parser.add_option("-q", "--quiet",
                      action="store_false")
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

    #OPEN OUTPUT FILE
    fOut = open(os.path.join(dctOptions.outputdir, dctOptions.outputname + ".cnv"), "w")
    
    fOut.write("FID\tIID\tCHR\tBP1\tBP2\tTYPE\tSCORE\tSITE\n")
    #LOAD DICTIONARIES    
    dctFamMap = utils.readFamFile(dctOptions.familyfile)
    if dctOptions.celmap:
        dctCelMap = utils.readCelMapFile(dctOptions.celmap)
    else:
        dctCelMap = {}
        
    #FIND PLATE FILES
    pattern = re.compile("[.]birdseye_calls", re.IGNORECASE)
    BirdsEyePaths = utils.findFiles(dctOptions.plateroot, pattern)
    #RUN PLATES
    for BirdsEyePath in BirdsEyePaths:
        BirdsEyeCallFile = open(BirdsEyePath)
        ReadPlateFile(BirdsEyeCallFile, fOut, dctOptions, dctFamMap, dctFamMissing, dctCelMap)
    
    #ERROR OUTPUT  
    if not dctOptions.quiet and len(dctFamMissing.keys()) > 0:
        print "\tFound individuals not in the Family Data:"
        for indiv in dctFamMissing.keys():
            print "\t" + indiv
    print "Finished -- Birdseye_To_Cnv.Py\n"

def ReadPlateFile(BirdsEyeCallFile, fOut, dctOptions, dctFamMap, dctFamMissing, dctCelMap):
    header_complete = False
    
    for strLine in BirdsEyeCallFile:
        Fields=strLine.split()
        
        if(header_complete == False):
            header_complete=True
            continue
        
        IID = utils.stripCelExt(Fields[0])
        if dctOptions.celmap:
            if dctCelMap.has_key(IID):
                IID = dctCelMap[IID]
        if dctFamMap.has_key(IID):
            FID = dctFamMap[IID][0]
        else:
            if not dctFamMissing.has_key(IID):
                dctFamMissing[IID] = True
            continue
        
        #DATA COLLECTION
        Type = Fields[2]
        Chrom = Fields[3]
        SPos = Fields[4]
        EPos = Fields[5]
        Score = Fields[9]
        if Score == '-Inf':
            Score = 0
            continue
        Site = Fields[8]
        if Site == '-Inf':
            Site = 0
            continue        
        
        fOut.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (FID,IID,Chrom,SPos,EPos,Type,Score,Site))  

if __name__ == "__main__":
    main()
    
