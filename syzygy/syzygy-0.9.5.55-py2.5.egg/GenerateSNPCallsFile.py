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
This script generates the output files for snplist (high quality) and snplist (poor quality)
Poor Quality : Median Fisher < .1 for SNP
"""

from __future__ import division
from optparse import OptionParser                                                                                                                                                                                                      
import sys,re
import numpy
from string import *
from SAMpileuphelper import *
import os
def main(argv=None):
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
    parser.add_option("--pif")
    parser.add_option("--hg")
    parser.add_option("--tgf")
    parser.add_option("--skipannot")
    parser.add_option("--samtoolspath")
    parser.add_option("--bqthr")
    parser.add_option("--ref")
    parser.add_option("--chr")
    parser.add_option("--ncpu")
    parser.add_option("--sndb")
    parser.add_option("--dbsnp")
    parser.add_option("--module")
    parser.add_option("--snplist",
                      default = "snplist.alleles.readyannot")
    parser.add_option("--outsnpcalls",
                      default = "PooledExperiment.snpcalls")
    
    parser.add_option("--outputdir")
    (options,args) = parser.parse_args()
  
    
    if not options.force:
        ###########################################################
        # Declare global variables: dbsnp dictionaries, mcrate dict.
        # Populate dbSNP dictionary. 
        ##########################################################
        
        snpsdetected = {}
        snplistfile = open(options.snplist,'r')
        snplistread = snplistfile.readlines()
        pathname = os.path.join(options.outputdir,str(options.outsnpcalls))
        outwritefile = open(pathname,'w')
        for snpline in snplistread[1:]:
            snpline = snpline.rstrip()
            snpline = snpline.split('\t')
            chr = snpline[1]
            pos = snpline[2]
            if "chr" in chr:
                chroffsetsnp = str(chr) + ':' + str(pos)
            else:
                chroffsetsnp = "chr" + str(chr) + ':' + str(pos)
            snpsdetected[chroffsetsnp] = chroffsetsnp
        
        id = 0
        snpcallsdict = {}
        poolfile = open(options.pif,'r')
        poolfile = poolfile.readlines()
        filedict = {}
        for linef in poolfile[1:]:
            linef = linef.rstrip()
            linef = linef.split()
           
            fname = linef[0] + str('.combined.error.coverage.calls')
            filedict[fname] = linef[0]
            filenamer = open(fname,'r')
            filenameread = filenamer.readlines()
            for line in filenameread[1:]:
                line = line.rstrip()
                line = line.split()
                if "chr" in line[0]:
                    chroffset = line[0]
                else:
                    chroffset = "chr" + line[0]
                snpcallsdict[chroffset,linef[0]] = line
                
            
       
        for key in snpsdetected.keys():
            for fname in filedict.keys():
                fnamekey = filedict[fname]
                fnamepool = fname.split('.')
                poolname = fnamekey
                outwritefile.write(str(poolname) + ' ') 
                if (key,fnamekey) in snpcallsdict:
                    for j in snpcallsdict[key,fnamekey]:
                        outwritefile.write(str(j) + ' ')
                    outwritefile.write('\n')
                else:
                    outwritefile.write('\n')
            outwritefile.write('\n\n')
            
            
                    
            
                        
            
            
if __name__ == "__main__":
    main()