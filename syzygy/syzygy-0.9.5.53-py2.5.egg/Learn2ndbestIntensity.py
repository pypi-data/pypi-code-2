#!/usr/bin/python

from __future__ import division

# Written by Manuel A. Rivas
# Updated 08.11.2009

# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2009 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$


from optparse import OptionParser
import array
import numpy
import math
import sys,re
from rpy2.rpy_classic import *
from SAMpileuphelper import *
import os

def main(argv = None):
    if not argv:
        argv = sys.argv
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)
    parser.add_option("-f","--force",
                      action="store_true",dest="force",
                      default=False,
                      help="proceed even with bad extensions")
    parser.add_option("--pif")
    parser.add_option("--hg")
    parser.add_option("--tgf")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--skipannot")
    parser.add_option("--module")
    parser.add_option("--chr")
    parser.add_option("--sndb")
    parser.add_option("--outputdir")
    parser.add_option("--bqthr", 
                      default = 22)
    parser.add_option("--mqthr",
                      default = 1)
    parser.add_option("--out",
                      default = "2ndbest.LOD")
    parser.add_option("--snplist",
                      default="snplist.alleles.readyannot")
    parser.add_option("--dbsnp",
                      default='/seq/dirseq/rivas/Rivasglioma/dbsnp/basepos.snpshg18.dbsnp')
    parser.add_option("--dosage",
                      default = "snps.dosage")
    (options, args) = parser.parse_args()
  
    if not options.force: 
        set_default_mode(BASIC_CONVERSION)  
        qthr = int(options.bqthr)
        mapqthr = int(options.mqthr)  
        snps = {}
        snpfile = open(options.snplist,'r')
        dbsnp = {}
        snpdet = {}  
        dbsnpfile = options.dbsnp
        dbsnp = populate_dbsnp_dictionary(dbsnp,dbsnpfile)
        snpfileread = snpfile.readlines()
        for snpline in snpfileread[1:]:
            snpline = snpline.rstrip()
            snpline = snpline.split('\t')
            chr = snpline[1]
            pos = snpline[2]
            chroffsetsnp = str(chr) + ':' + str(pos)
            snps[chroffsetsnp] = chroffsetsnp
            snpdet[chroffsetsnp,'ref'] = snpline[5][0]
            snpdet[chroffsetsnp,'alt'] = snpline[5][1]
          
        snplod = {}
        secondlod = {}
        pifpath = os.path.join(options.outputdir,options.pif)
        pifread = open(pifpath,'r').readlines()
        for line in pifread[1:]:
            line = line.rstrip()
            line = line.split()
            pool = line[0]
            phenotype = line[1]
            inds = line[2]
            chroms = line[3]
            callsf = str(pool) + '.combined.error.coverage.calls'
            callspath = os.path.join(options.outputdir,callsf)
            callsread = open(callspath,'r').readlines()
          
#===============================================================================
#      Read in Calls file to get LOD of SNP detection
#===============================================================================
            print "Processing Pool %s Calls File"  % (str(pool))
            for line in callsread[1:]:
                line = line.rstrip()
                line = line.split()
                chroffset = line[0]
                lod = line[21]
                if chroffset in snps:
                    snplod[pool,chroffset] = lod
                    
            
            
            pileupf = str(pool) + '.pileup'
            poolpileuppath = os.path.join(options.outputdir,pileupf)
            poolpileupread = open(poolpileuppath,'r')     
        
#===============================================================================
#        Read in PIF File for Pileup Analysis 
#===============================================================================
            print "Processing 2ndBest Base %s Pileup File"  % (str(pool))
            for line in poolpileupread:
                line = line.rstrip()
                line = line.split('\t')
                chr = line[0]
                position = int(line[1]) 
                if "chr" in chr:
                    chroffset =  str(chr) + ":" + str(position)
                else:
                    chroffset = "chr" + str(chr) + ":" + str(position)
               
                if chroffset in snps:
                    reference_allele = line[2]
                    reference_allele = reference_allele.upper()
                    if reference_allele == 'A':
                        ref_index = 0
                    elif reference_allele == 'C':
                        ref_index = 1
                    elif reference_allele == 'G':
                        ref_index = 2
                    elif reference_allele == 'T':
                        ref_index = 3
                    coverage = line[3]
                    allele_calls = line[4]
                    base_quals = line[5]
                    map_quals = line[8]
                    sndbestid = line[6]
                    sndbestquals = line[7]
                    map_quals_list = list(map_quals)
                    base_quals_list = list(base_quals)
                    allele_calls_list =list(allele_calls)
                    sndbestlist = list(sndbestid)
                    sndbestlistquals = list(sndbestquals)
                    map_quals_strings = ascii_list(map_quals_list)
                    base_quals_strings = ascii_list(base_quals_list)
                    snd_quals_strings = ascii_list(sndbestlistquals)
                    allele_calls_strings = allele_calls_list
                    base_qualsthreshold_strings = return_q_list(qthr,base_quals_strings)
                    if (pool,chroffset) in snplod:
                        if snplod[pool,chroffset] >= 3:
                            allele_calls_threshold_strings = return_alleleq_list_SAM(mapqthr,qthr,base_quals_strings,map_quals_strings,allele_calls_strings)
                            (allelethrstring,sndthrlst) = return_snd_list_SAM(mapqthr,qthr,base_quals_strings,map_quals_strings,allele_calls_strings,sndbestlist)
                            if (chroffset,'fwd') in secondlod:
                                secondlod[chroffset,'fwd'] += computesndLODfwd(allelethrstring,sndthrlst,secondlod[chroffset,'fwd'],snpdet[chroffset,'ref'],snpdet[chroffset,'alt'])
                                secondlod[chroffset,'rev'] += computesndLODrev(allelethrstring,sndthrlst,secondlod[chroffset,'rev'],snpdet[chroffset,'ref'],snpdet[chroffset,'alt'])
                            else:
                                secondlod[chroffset,'fwd'] = 0
                                secondlod[chroffset,'rev'] = 0
                                secondlod[chroffset,'fwd'] += computesndLODfwd(allelethrstring,sndthrlst,secondlod[chroffset,'fwd'],snpdet[chroffset,'ref'],snpdet[chroffset,'alt'])
                                secondlod[chroffset,'rev'] += computesndLODrev(allelethrstring,sndthrlst,secondlod[chroffset,'rev'],snpdet[chroffset,'ref'],snpdet[chroffset,'alt'])
                                
        snpfiler = open(options.snplist,'r')
        snpfilerd = snpfiler.readlines()
        sndlodout = os.path.join(options.outputdir,'sndlod.2b')
        sndlodwrite = open(sndlodout,'w+')
        for snplineread in snpfilerd[1:]:
            snpline = snplineread.rstrip()
            snpline = snplineread.split('\t')
            chr = snpline[1]
            pos = snpline[2]
            chroffsetsnp = str(chr) + ':' + str(pos)
            if (chroffsetsnp,'fwd') in secondlod and (chroffsetsnp,'rev') in secondlod:
                combinedsnd = secondlod[chroffsetsnp,'fwd'] + secondlod[chroffsetsnp,'rev']
            elif (chroffsetsnp,'fwd') in secondlod: 
                combinedsnd = float(secondlod[chroffsetsnp,'fwd']) + 0
                secondlod[chroffsetsnp,'rev'] = 0
            elif (chroffsetsnp,'rev') in secondlod:
                combinedsnd = float(secondlod[chroffsetsnp,'rev']) + 0
                secondlod[chroffsetsnp,'fwd'] = 0
            else:
                combinedsnd = 0
                secondlod[chroffsetsnp,'fwd'] = 0
                secondlod[chroffsetsnp,'rev'] = 0
            sndlodwrite.write(str(chroffsetsnp) + ' ' + str(secondlod[chroffsetsnp,'fwd']) + ' ' + str(secondlod[chroffsetsnp,'rev']) + ' ' + str(combinedsnd) + '\n')
        
if __name__ == "__main__":
    main()