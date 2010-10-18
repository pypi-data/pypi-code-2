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
def main(argv=None):
    if not argv:
        argv = sys.argv
    usage = "usage: %prog [options]"
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
    parser.add_option("--skipannot")
    parser.add_option("--ncpu")
    parser.add_option("--dbsnp")
    parser.add_option("--bqthr")
    parser.add_option("--sndb")
    parser.add_option("--module")
    parser.add_option("--chr")

    parser.add_option("--dosage",
                      default = "snps.dosage.pool")
    parser.add_option("--summary",
                      default = "PooledExperiment.summary")
    parser.add_option("--snpcalls",
                      default = "PooledExperiment.snpcalls")
    parser.add_option("--out",
                      default = "PooledExperiment.pbp")
    parser.add_option("--outputdir")
    (options, args) = parser.parse_args()


    if not options.force:
    	pooldict = {}
        poollist = {}
        snpfile = open(options.snpcalls,'r').readlines()
        for line in snpfile[1:]:
            line = line.rstrip()
            line = line.split()
            if len(line) > 10:
                pool = line[0]
                poollist[pool] = pool
                lod = line[22]
                conv = str(line[17]) + str(line[18])
                chroffset = line[1]
                if "chr" in chroffset:
                    pass
                else:
                    chroffset = "chr" + str(chroffset)
               # pooldict[chroffset,'pool'] = pool
                pooldict[chroffset,pool,'lod'] = lod
                pooldict[chroffset,pool,'conv'] = conv
                
        summaryfile = open(options.summary,'r').readlines()
        snpsdict = {}
        snps = {}
        for summaryline in summaryfile[1:]:
            summaryline = summaryline.rstrip()
            summaryline = summaryline.split()
            if len(summaryline) == 17:
                chroffset = summaryline[0]
                if "chr" in chroffset: 
                    pass
                else:
                    chroffset = "chr" + str(chroffset)
                alleles = summaryline[1]
                type = summaryline[3]
                rs = summaryline[4]
                Slod = summaryline[15]
                fisher = summaryline[16]
                snpsdict[chroffset,'type'] = type
                snpsdict[chroffset,'rs'] = rs
                snpsdict[chroffset,'fisher'] = float(fisher)
                snpsdict[chroffset,'S'] = float(Slod)
                snpsdict[chroffset,'alleles'] = alleles
                snps[chroffset] = chroffset
        outwrite = open(options.out,'w+')
        outwrite.write('Pool/Type High(S < 0) Med(0<=S<=5) Low(S>=5)\n')
        for pool in poollist.keys():
            pooldb = [0,0,0]
            poolnondb = [0,0,0]
            poolns = [0,0,0]
            poolsyn = [0,0,0]
            transitions  = [0,0,0]
            transversions = [0,0,0]
            poolcnt = 0
            poolcntq = [0,0,0]
            for key in snps.keys():
                if (key,pool,'lod') in pooldict:
                    if float(pooldict[key,pool,'lod']) >= 3:
                        poolcnt += 1

                        if snpsdict[key,'S'] < 0 and snpsdict[key,'fisher'] >= .1:
                            poolcntq[0] += 1
                            if "rs" in snpsdict[key,'rs']:
                                pooldb[0] += 1
                            else:
                                poolnondb[0] += 1 
                            if checktransitiontransversion(snpsdict[key,'alleles']) == 1:
                                transitions[0] += 1
                            else:
                                transversions[0] += 1
                        
                            if snpsdict[key,'type'] == 'ns':
                                poolns[0] += 1
                            elif snpsdict[key,'type'] == 's':
                                poolsyn[0] += 1
                        elif snpsdict[key,'S'] >= 0 and snpsdict[key,'S'] <= 5 and snpsdict[key,'fisher'] >= .1:
                            poolcntq[1] += 1
                            if "rs" in snpsdict[key,'rs']:
                                pooldb[1] += 1
                            else:
                                poolnondb[1] += 1 
                            if checktransitiontransversion(snpsdict[key,'alleles']) == 1:
                                transitions[1] += 1
                            else:
                                transversions[1] += 1
    	                    if snpsdict[key,'type'] == 'ns':
                                poolns[1] += 1
                            elif snpsdict[key,'type'] == 's':
                                poolsyn[1] += 1
                        elif snpsdict[key,'S'] > 5 or snpsdict[key,'fisher'] > .1:
                            poolcntq[2] += 1
                            if "rs" in snpsdict[key,'rs']:
                                pooldb[2] += 1
                            else:
                                poolnondb[2] += 1 
                            if checktransitiontransversion(snpsdict[key,'alleles']) == 1:
                                transitions[2] += 1
                            else:
                                transversions[2] += 1
                            if snpsdict[key,'type'] == 'ns':
                                poolns[2] += 1
                            elif snpsdict[key,'type'] == 's':
                                poolsyn[2] += 1
            outwrite.write(str(pool) +'\n')
            outwrite.write(("Counts- %4.4g\n") % (poolcnt) )
            outwrite.write(("Counts-%4.4g %4.4g %4.4g\n") % (poolcntq[0],poolcntq[1],poolcntq[2]))
            dbratio = [pooldb[i]/(poolnondb[i] + pooldb[i] + .000001) for i in range(0,len(pooldb))]
    	    nssratio = [poolns[i]/(poolsyn[i] + .000001) for i in range(0,len(poolns))]
            tstratio = [transitions[i]/(transversions[i] + .000001) for i in range(0,len(transitions))]
            outwrite.write(("dbSNP- %4.4g %4.4g %4.4g\n") % (dbratio[0]*100,dbratio[1]*100,dbratio[2]*100) )
            outwrite.write(("NS/S- %4.4g %4.4g %4.4g\n") % (nssratio[0],nssratio[1],nssratio[2]))
            outwrite.write(("TS/T- %4.4g %4.4g %4.4g\n") % (tstratio[0],tstratio[1],tstratio[2]))
            
if __name__ == "__main__":
    main()