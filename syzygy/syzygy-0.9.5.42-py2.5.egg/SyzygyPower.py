
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

### Pooled Sequencing Analysis

from optparse import OptionParser
import array
import numpy
import math
import sys,re
import rpy2
from rpy2.rpy_classic import *
from SAMpileuphelper import *
import pp
import time
import os
from os import popen

def main(argv=None):
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
    parser.add_option("--ncpu",
                      default = 1)
    parser.add_option("--module")
    parser.add_option("--skipannot")
    parser.add_option("--chr")
    
    parser.add_option("--mqthr")
    parser.add_option("--sndb")
    parser.add_option("--dbsnp")
    parser.add_option("--bqthr")
    parser.add_option("--out",
                      default = "PooledExperiment.pf")
    parser.add_option("--outputdir")
    (options, args) = parser.parse_args()


    if not options.force:
        set_default_mode(BASIC_CONVERSION)
        ppservers = ()
        ncpus = int(options.ncpu)
        job_server = pp.Server(ncpus,ppservers=ppservers)
        jobs = []
        powerdict = {}
        exonfile = options.tgf
        exonf = open(exonfile,'r')
        exonf = exonf.readlines()
        poolfile = open(options.pif,'r')
        poolfile = poolfile.readlines()
        poollist = []
        for linef in poolfile[1:]:
            linef = linef.rstrip()
            linef = linef.split()
            poolbam = linef[0]
            poollist.append(poolbam)
            phenotype = int(linef[1])
            inds = int(linef[2])
            chromosomes = int(linef[3])
            inputefile = str(poolbam) + '.combined.error.coverage'
            
            jobs.append(job_server.submit(EvaluatePower,(inputefile,exonfile,chromosomes,powerdict),(),("math","numpy","rpy2.rpy_classic","rpy2")))
        start_time = time.time()
        for job in jobs:
            result = job()
            for key in result.keys():
                powerdict[key] = result[key]
            
        
        print "Time elapsed: ", time.time() - start_time, "s"
        print powerdict.keys()
        job_server.print_stats()
                            
##########################################################################################
#
# Go through all the targeted exons, amplicon details file, plate(in experiment file)
#########################################################################################
       


       
        summaryf = options.out
        summarywriteexon = open(summaryf,'w')
        summarywriteexon.write('chr:offset target_id ')
        for pool in poollist:
            summarywriteexon.write(str(pool) + ' ')
        summarywriteexon.write('\n')
        for exonline in exonf[1:]:
            exonline = exonline.split()
            target = exonline[0]
            chr = exonline[1]
            start = int(exonline[2])
            stop = int(exonline[3])
            size = int(exonline[4])
    
            if start < stop:
                beg = start -5
                end = stop + 5
            elif stop < start:
                beg = stop -5 
                end = start + 5
            rangelist = r.seq(beg,end,1)

          
            for pos in rangelist:
                if "chr" in chr:
                    chroffset = str(chr) + ":" + str(pos)
                else:
                    chroffset = "chr" + str(chr) + ":" + str(pos)
                summarywriteexon.write(str(chroffset) + ' ' + str(target) + ' ')
                for pool in poollist:
                    errorfile = pool + '.combined.error.coverage'
                    summarywriteexon.write(("%4.4g ")  % (float(powerdict[errorfile,chroffset])))
                summarywriteexon.write('\n')

def EvaluatePower(errorfile,targetfile,chroms,powerdictfinal):
    import rpy2.robjects as robjects
    from rpy2.rpy_classic import *
    set_default_mode(BASIC_CONVERSION)
    coveragemap = {}
    fileopen = open(errorfile,'r').readlines()
    for line in fileopen[1:]:
        line = line.rstrip()
        line = line.split()
        chr = line[0]
        offset = line[1]
        chroffset = line[2]
        ref_base = line[3]
        ref_idx = line[4]
        fwdcovg = sum([int(i) for i in line[5:11]])
        revcovg = sum([int(i) for i in line[12:18]])
        mcratefwd = float(line[11])
        mcraterev = float(line[18])
        coveragemap[errorfile,chroffset,'coverage'] = fwdcovg + revcovg
        coveragemap[errorfile,chroffset,'coveragefwd'] = fwdcovg
        coveragemap[errorfile,chroffset,'coveragerev'] = revcovg
        coveragemap[errorfile,chroffset,'mcratefwd'] = mcratefwd
        coveragemap[errorfile,chroffset,'mcraterev'] = mcraterev
        
  
    
    
    exonf = open(targetfile,'r')
    exonf = exonf.readlines()
    for exonline in exonf[1:]:
   
        exonline = exonline.split()
        target = exonline[0]
        chr = exonline[1]
        start = int(exonline[2])
        stop = int(exonline[3])
        size = int(exonline[4])

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
            
            if (errorfile,chroffset,'coverage') in coveragemap:
                rejectn = 0
                robjects.globalEnv["reject"] = rejectn
                robjects.globalEnv["covfwd"] = coveragemap[errorfile,chroffset,'coveragefwd']
                robjects.globalEnv["covrev"] = coveragemap[errorfile,chroffset,'coveragerev']
                robjects.globalEnv["mcfwd"] = coveragemap[errorfile,chroffset,'mcratefwd']
                robjects.globalEnv["mcrev"] = coveragemap[errorfile,chroffset,'mcraterev']
                robjects.globalEnv["chromosomes"] = chroms
#===============================================================================
#                r.assign("reject",rejectn)
#                r.assign("covfwd",coveragemap[errorfile,chroffset,'coveragefwd'])
#                r.assign("covrev",coveragemap[errorfile,chroffset,'coveragerev'])
#                r.assign("mcfwd",coveragemap[errorfile,chroffset,'mcratefwd'])
#                r.assign("mcrev",coveragemap[errorfile,chroffset,'mcraterev'])
#                r.assign("chromosomes",chroms)
#===============================================================================
                robjects.r('for(i in 1:300){sfwd<-sample(chromosomes,covfwd,replace=TRUE);nonreffwd<-dim(as.matrix(sfwd[sfwd == 1]))[1];srev<-sample(chromosomes,covrev,replace=TRUE);nonrefrev<-dim(as.matrix(srev[srev == 1]))[1];LOD<-log10(dbinom(nonreffwd,covfwd,1/chromosomes)) + log10(dbinom(nonrefrev,covrev,1/chromosomes)) - log10(dbinom(nonreffwd,covfwd,mcfwd)) - log10(dbinom(nonrefrev,covrev,mcrev));if(LOD >= 3){reject = reject+ 1;}}')
                powereval = math.ceil((float(robjects.r['reject'][0])/300)*100)
                pfwd = robjects.r['covfwd']
                frev = robjects.r['covrev']
                mcf = robjects.r['mcfwd']
                mcr = robjects.r['mcrev']
#===============================================================================
#                del r.reject
#                del r.covfwd
#                del r.covrev
#                del r.mcfwd
#                del r.mcrev
#===============================================================================
                
                    
                robjects.r.remove(list= robjects.r.objects())
            else:
                powereval = 0
            powerdictfinal[errorfile,chroffset] = powereval
    return powerdictfinal
                
        
if __name__ == "__main__":
    main()


