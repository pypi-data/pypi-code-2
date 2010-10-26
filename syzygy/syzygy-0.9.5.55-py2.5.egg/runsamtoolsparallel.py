#!/usr/bin/python


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



import optparse
from mpgutils import utils                                                                                                                                                                                                   
import sys,re
from optparse import OptionParser
import os
import subprocess
import pp
import time

def main(argv = None):
    if not argv:
        argv = sys.argv
    lstRequiredOptions = ["tgf", "pif","ref"]
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)
    #REQUIRED Commands
    parser.add_option("-s","--samtoolspath", 
                      help="Samtools Path")
    parser.add_option("-f","--ref", 
                      help="Reference Fasta File")
    parser.add_option("-i","--pif",
                      help="Pool Info File")
    parser.add_option("-t","--tgf",
                      help = "Target Info File")
    parser.add_option("--outputdir")
    parser.add_option("--bqthr")
    parser.add_option("--mqthr")
    parser.add_option("--chr")
    parser.add_option("--ncpu")
    parser.add_option('-n',"--sndb",
                      help = "Specifiy Noise Annotation (true or false)")
    
    #["--samtoolspath","hgbuild","reference", "target", "positionfile", poolinfofile]
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    #*** SYSTEM CALLS ***
    #FIND EGGS
    #Eggs = findFiles(dctOptions.eggdir, re.compile("[.]egg", re.IGNORECASE))
    samtoolspath = os.path.expanduser(dctOptions.samtoolspath)
    if not os.path.exists(samtoolspath):
        samtoolspath, tempexe = os.path.split(samtoolspath)
        if os.path.exists(samtoolspath):
            samtoolsexe = findFiles(samtoolspath, re.compile(tempexe, re.IGNORECASE))
            if samtoolsexe:
                samtools = samtoolsexe[0]
        else:
            print "Could not locate Sam Tools"
            sys.exit(1)
    else:
        samtools = os.path.join(samtoolspath, "samtools")
    
    poolfile = open(os.path.expanduser(dctOptions.pif),'r')
    poolfile = poolfile.readlines()
#    test_call()
    ppservers = ()
    ncpus = int(dctOptions.ncpu)
    job_server = pp.Server(ncpus,ppservers=ppservers)
    jobs = []
    for line in poolfile[1:]:
        line = line.rstrip()
        line = line.split()
        bamfile = line[0]
        lstArgs = [samtools,"pileup", "-l",dctOptions.tgf + str(".cif"), "-f",dctOptions.ref ,bamfile]
        lstArgs.append("-s")
        if dctOptions.sndb == "true":
            lstArgs.append("-2")
        
        lstArgs.append(os.path.join(dctOptions.outputdir,str(bamfile) + ".pileup" ))
        jobs.append(job_server.submit(check_call,(lstArgs,),(),("subprocess",)))

    start_time = time.time()
    for job in jobs:
        result = job()
        if result:
            break
    print "Time elapsed: ", time.time() - start_time, "s"
    job_server.print_stats()
       
def findFiles(folder_root, pattern):
    Files = []
    for root, dirs, files in os.walk(folder_root, False):
        for name in files:
            match = pattern.search(name)
            if match:
                Files.append(os.path.join(root, name))
    return Files

def check_call(lstArgs):
    print lstArgs[-1]
    retcode = subprocess.Popen(lstArgs[0:len(lstArgs)-1],stdout=file(lstArgs[-1],"w"))
    retcode.wait()
    #if retcode != 0:
    #    raise Exception("ERROR: exit status %d from command %s" % (retcode, " ".join(lstArgs)))
    #    sys.exit(retcode)
        
#def test_call():
#
#    proc = subprocess.Popen(
#    '/seq/dirseq/samtools/current/samtools pileup -l crohns.exonfile.tgf.cif -f /home/radon00/rivas/bin/Syzygy/trunk/reference/hg17.fasta  5_NJCDCASES.merged.bam -s  > 5_NJCDCASES.merged.bam.pileup',
#    shell=True,
#    stdin=subprocess.PIPE  )
#    print 'process created'
        
    
    #Call on validate path, with a set of options
    
if __name__ == "__main__":
    main()