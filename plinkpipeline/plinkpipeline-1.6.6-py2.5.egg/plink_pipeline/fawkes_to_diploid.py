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

Convert larry_bird-style calls file into conventional diploid calls file, with calls represented as
0 (AA or A for haploid SNP); 1 (AB); 2 (BB or B for haploid SNP), -1 (no call),
replacing all calls of unusual copy number with no-call (-1).
"""

from __future__ import division
import os, re
import optparse
import sys
import diploid_calls_filter
from mpgutils import utils

def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    lstRequiredOptions = ["plateroot", "metadir"]
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-p", "--plateroot",
                      help="""(Required) The Root folder which contains Output calls file in traditional apt-probeset-genotype format.""")
    parser.add_option("-x", "--metadir", 
                      help="(Required) Meta_directory with special snps")
    parser.add_option("-c", "--chip", default=6, help="Chip Type")
    parser.add_option("--expected_cn_snps", help="""If present, write all the SNPs for which all samples have
                        expected copy number.""")
    parser.add_option("--unexpected_cn_snps", help="""If present, write all the SNPs for which at least one
                        sample has unexpected copy number.""")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    #VALIDATE PATHS
    lstOptionsToCheck = ['plateroot', 'metadir']
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    #CHECK PLATE PATHS
    pattern = re.compile('[.]merged[.]fawkes[.]calls', re.IGNORECASE)
    CallsPaths = utils.findFiles(dctOptions.plateroot, pattern) 
    pattern = re.compile('[.]merged[.]gen', re.IGNORECASE)
    GenderPaths = utils.findFiles(dctOptions.plateroot,pattern)
    if len(CallsPaths) != len(GenderPaths):
        print "There are missing gender files, please ensure each plate has a gender file."
        print "If you have not built your gender files, please use --buildgender and then continue "
        sys.exit(1)
    
    #SPECIAL SNPS
    pattern = re.compile(str(dctOptions.chip) + '[.]specialSNPs', re.IGNORECASE)
    SpecialSnps = utils.findFiles(dctOptions.metadir,pattern)
    if not SpecialSnps:
        print "Could not find Special SNPs"
        sys.exit(1)
    
    #CALLS FILES
    MakeDiploidFiles(CallsPaths, GenderPaths, SpecialSnps, dctOptions)
    print "Finished -- Fawkes_To_Diploid.Py\n"
    
def MakeDiploidFiles(CallsPaths, GenderPaths, SpecialSnps, dctOptions):

    for i, CallsFile in enumerate(CallsPaths):
        
        diploidCallsFilter = diploid_calls_filter.Filter(GenderPaths[i],SpecialSnps[0])
        fIn = open(CallsFile)
        
        #OUTPUT FILE NAMES
        out_path,out_file = os.path.split(CallsFile)
        file_name = out_file.split(".")
        out_file = file_name[0] + '.merged.diploid' 
        fOut = open(os.path.join(out_path, out_file), "w")
        
        #EXPTECTED FILES
        if dctOptions.expected_cn_snps is not None:
            fExpectedCNSNPs = open(dctOptions.expected_cn_snps, "w")
        else:
            fExpectedCNSNPs = None
        if dctOptions.unexpected_cn_snps is not None:
            fUnexpectedCNSNPs = open(dctOptions.unexpected_cn_snps, "w")
        else:
            fUnexpectedCNSNPs = None

        #MAKE HEADER
        strHeader = utils.skipHeader(fIn, "probeset_id")
        if diploidCallsFilter.numSamples() + 1 != len(strHeader.split()):
            raise Exception("Number of entries in gender file does not agree with number of columns in calls file")
    
        #WRITE DIPLOID FILE
        fOut.write(strHeader)
        for strLine in fIn:
            lstFields = strLine.split()
            strSNP = lstFields[0]
            del lstFields[0]
            lstFilteredCalls = diploidCallsFilter.filterCalls(strSNP, lstFields)
    
            #WRITE OUTPUT
            print >>fOut, "\t".join([strSNP] + [str(val) for val in lstFilteredCalls])
        
        #OPTIONAL OUTPUTS
        if fExpectedCNSNPs is not None:
            for strSNP in diploidCallsFilter.lstExpectedSNPs:
                print >>fExpectedCNSNPs, strSNP
        if fUnexpectedCNSNPs is not None:
            for strSNP in diploidCallsFilter.lstUnexpectedSNPs:
                print >>fUnexpectedCNSNPs, strSNP
    
        fOut.close()
        fIn.close()
        if fExpectedCNSNPs is not None:
            fExpectedCNSNPs.close()
        if fUnexpectedCNSNPs is not None:
            fUnexpectedCNSNPs.close()
        
if __name__ == "__main__":
    sys.exit(main())
    
