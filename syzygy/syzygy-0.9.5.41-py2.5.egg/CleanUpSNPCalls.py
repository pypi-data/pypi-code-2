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
    parser.add_option("--module")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--bqthr")
    parser.add_option("--chr")
    parser.add_option("--sndb")
    parser.add_option("--skipannot")

    parser.add_option("--out",
                      default = "snplist.alleles")
    (options,args) = parser.parse_args()
    
    if not options.force:
        ###########################################################
        # Declare global variables: dbsnp dictionaries, mcrate dict.
        # Populate dbSNP dictionary. 
        ##########################################################
        
        dbsnp = {}
        exptchroffsets = {}
        accumcoveragefwd = {}
        accumcoveragerev = {}
        mcratefwd = {}
        mcraterev = {}
        refalleles = {}
        pools = 0 # Set Pool Counter to 0
        pathnamehigh = os.path.join(options.outputdir,str(options.out) +'.high' )
        pathnamepoor = os.path.join(options.outputdir,str(options.out) + '.poor')
        pathnameannot = os.path.join(options.outputdir,str(options.out) + '.readyannot')
        goodsnplist = open(pathnamehigh,'w')
        poorsnplist = open(pathnamepoor,'w')
        annotationfile = open(pathnameannot,'w')
        dbsnpfile = options.dbsnp
        dbsnp = populate_dbsnp_dictionary(dbsnp,dbsnpfile)
        hgbuild = int(options.hg)
        annot = {}
        ########################################################
        # Accumulate Calls
        #
        snps = {}
        annotationfile.write("id\tchromosome\tposition\tgenome\torientation\talleles\n")
        id = 0
        candidatesites = {}
        exonf = open(options.tgf,'r')
        exonf = exonf.readlines()
        for exonline in exonf[1:]:
            exonline = exonline.split()
            target = exonline[0]
            chr = exonline[1]
            start = int(exonline[2])
            stop = int(exonline[3])
            
            
            if start < stop:
                beg = start -5
                end = stop + 5
            elif stop < start:
                beg = stop - 5 
                end = start + 5
            rangelist = r.seq(beg,end,1)
            for pos in rangelist:
                if "chr" in chr:
                    chroffset = str(chr) + ":" + str(pos)
                else:
                    chroffset = "chr" + str(chr) + ":" + str(pos)
                candidatesites[chroffset] = chroffset
        poolfile = open(options.pif,'r')
        poolfile = poolfile.readlines()
        for linef in poolfile[1:]:
            linef = linef.rstrip()
            linef = linef.split()
            fname = str(linef[0]) + '.combined.error.coverage.calls'
            filenamer = open(fname,'r')
            filenameread = filenamer.readlines()
            for line in filenameread[1:]:
                line = line.rstrip()
                line = line.split()
                if "chr" in line[0]:
                    chroffset = line[0]
                else:
                    chroffset = "chr" + str(line[0])
                ref_base = line[1]
                ref_allele = str(line[16])
                alt_allele = str(line[17])
                allelespos = str(ref_allele) + str(alt_allele)
                coverage = int(line[18])
                lodfwd = float(line[19])
                lodrev = float(line[20])
                lod = float(line[21])
                fisherflag = line[22]
                if fisherflag == "NA":
                    pass
                elif fisherflag == "***":
                    fisherpval = float(line[23])
                
                if lod >= 3 and coverage >= 100:
                    if fisherflag == "NA":
                        fisherpval = 1
                    if chroffset in annot:
                        annot[chroffset].append(allelespos)
                            
                    else:
                        annot[chroffset] = []
                        annot[chroffset].append(allelespos)
                    if chroffset in snps:
                        snps[chroffset].append(fisherpval)
                    else:
                        snps[chroffset] = []
                        snps[chroffset].append(fisherpval)
                elif lod >= 3 and chroffset in snps:
                    snps[chroffset].append(fisherpval)
                        
        for key in snps.keys():
            medpval = float(numpy.median(snps[key]))
            if medpval > .1 and key in candidatesites:
                id += 1
                goodsnplist.write(str(key) + ' ' + str(medpval) + ' '  )
                for i in snps[key]:
                    goodsnplist.write(str(i) + ' ' )
                goodsnplist.write('\n')
                alleles = [j for j in set(annot[key])]
                (chr,position) = key.split(":")
                for allele in alleles:
                    if "chr" in chr:
                        pass
                    else:
                        chr = str("chr") + str(chr)
                    
                    annotationfile.write(str(id) + '\t' + str(chr) + '\t' + str(position) + '\t' + 'HG' + str(options.hg) + '\t' + 'F' + '\t' + str(allele) + '\n'  )
            elif medpval <= .1 and key in candidatesites:
                id += 1
                poorsnplist.write(str(key) + ' ' + str(medpval) + ' ' )
                for i in snps[key]:
                    poorsnplist.write(str(i) + ' ' )
                poorsnplist.write('\n')
                alleles = [j for j in set(annot[key])]
                (chr,position) = key.split(":")
                for allele in alleles:
                    if "chr" in chr:
                        pass
                    else:
                        chr = str("chr") + str(chr)
                    
                    annotationfile.write(str(id) + '\t' + str(chr) + '\t' + str(position) + '\t' + 'HG' + str(options.hg) + '\t' + 'F' + '\t' + str(allele) + '\n'  )
            else:
                pass  
                    
            
                        
            
            
if __name__ == "__main__":
    main()