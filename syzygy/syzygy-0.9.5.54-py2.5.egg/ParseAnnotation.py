#!/usr/bin/env python

# Written by Manuel A. Rivas
# Updated 07.13.2009

# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2009 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$



"""
This script Parses the Annotation Output from the Server
"""

from __future__ import division
from optparse import OptionParser                                                                                                                                                                                                      
import sys,re
import numpy
from string import *
from SAMpileuphelper import *
import os
def main(argv = None):
    if not argv:
        argv = sys.argv
    #####################################################
    # Define arguments and options.
    #####################################################
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)
    parser.add_option("-f","--force",
                      action="store_true",dest="force",
                      default=False,
                      help="proceed even with bad extensions")
    parser.add_option("--dbsnp",
                      default="/seq/dirseq/rivas/Rivasglioma/dbsnp/basepos.snpshg18.dbsnp")
    parser.add_option("--hg",
                      default = 18)
    parser.add_option("--outputdir")
    parser.add_option("--pif")
    parser.add_option("--tgf")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--bqthr")
    parser.add_option("--skipannot")
    parser.add_option("--chr")
    parser.add_option("--module")
    parser.add_option("--sndb")
    parser.add_option("--annot",
                      default = "snps.annotation.full.1")
    parser.add_option("--out",
                      default = "snplist.alleles")
    (options,args) = parser.parse_args()
    
    if not options.force:
        pathnameannot = os.path.join(options.outputdir,str(options.annot))
        annotfile = open(pathnameannot,'r').readlines()
        nspath = os.path.join(options.outputdir,'snplist.alleles.ns')
        synpath = os.path.join(options.outputdir,'snplist.alleles.syn')
        ncpath = os.path.join(options.outputdir,'snplist.alleles.nc')
        utrpath = os.path.join(options.outputdir,'snplist.alleles.utr')
        utrncntpath = os.path.join(options.outputdir,'snplist.alleles.utrncnt')
        synwrite = open(synpath,'w')
        utrwrite = open(utrpath,'w')
        utrncntwrite = open(utrncntpath,'w')
        ncwrite = open(ncpath,'w')
        nswrite = open(nspath,'w')
        
        for line in annotfile[1:]:
            line = line.rstrip()
            line = line.split('\t')
            
            chromosome = line[1]
            position = line[2]
            
            observedallele = line[3]
            referenceallele = line[4]
            

            if len(line) > 13:
                transcriptaccession = line[7] 
                transcriptorientation = line[8]
                splicedistance = line[9]
                intranscript = line[10]
                incodingregion = line[12]
                dbsnp = line[5]
                genename = line[6]
                refcodon = line[15]
                refamino = line[16]
                codonnumber = line[14]
                variantcodon = line[18]
                variantamino = line[19]
                changesamino = line[20]
                if incodingregion == 'true' and not refcodon == variantcodon and changesamino == 'true':
                    nswrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(genename) + ' ' + str(refcodon) + str(codonnumber) + str(variantcodon) + ' ' + str(refamino) + str(codonnumber) + str(variantamino) + ' ' + str(dbsnp) + '\n')
                elif incodingregion == 'true' and not refcodon == variantcodon and changesamino == 'false':
                    synwrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(genename) + ' ' + str(refcodon) + str(codonnumber) + str(variantcodon) + ' ' + str(refamino) + str(codonnumber) + str(variantamino) + ' ' + str(dbsnp) + '\n')
                elif refcodon == variantcodon:
                    pass
            elif len(line) > 6:
                transcriptaccession = line[7] 
                transcriptorientation = line[8]
                splicedistance = line[9]
                intranscript = line[10]
                incodingregion = line[12]
                genename = line[6]
                dbsnp = line[5]
                if incodingregion == 'false' and intranscript == 'true':
                    utrwrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(genename) + ' ' + str(observedallele) + ' ' + str(transcriptaccession) + ' ' + str(transcriptorientation) + ' ' + str(splicedistance) + ' ' + str(dbsnp) + '\n')
                elif incodingregion == 'false' and intranscript == 'false':
                    utrncntwrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(genename) + ' ' + str(observedallele) + ' ' + str(referenceallele) + ' ' + str(transcriptaccession) + ' ' + str(transcriptorientation) + ' ' + str(splicedistance) + ' ' + str(dbsnp) + '\n')
                elif len(genename) < 1:
                    ncwrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(observedallele) + ' ' + str(referenceallele) + ' ' + str(dbsnp) + '\n')
            else:
                if len(line) == 6:
                    ncwrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(observedallele) + ' ' + str(referenceallele) + ' ' + str(dbsnp) + '\n')
                else:
                    ncwrite.write(str(chromosome) + ' ' + str(position) + ' ' + str(observedallele) + ' ' + str(referenceallele) + ' ' + ' ' + '\n')
    
        synwrite.close()
        utrwrite.close()
        nswrite.close()
        utrncntwrite.close()
        ncwrite.close()
    
            
if __name__ == "__main__":
    main()