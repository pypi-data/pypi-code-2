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

def main(argv = None):
    if not argv:
        argv = sys.argv
    
    
    
    
    #*** SYSTEM CALLS ***
    #FIND EGGS
    #Eggs = findFiles(dctOptions.eggdir, re.compile("[.]egg", re.IGNORECASE))
    perlpath = os.path.join("/home/radon00/rivas/bin/syzygyfinal/trunk/playground/Syzygy/perl/", "ParseAnnotationOutput.pl")
    perlp = os.path.join("/util/bin/","perl")
    lstArgs = [perlp,perlpath]
    check_call(lstArgs)
       
def findFiles(folder_root, pattern):
    Files = []
    for root, dirs, files in os.walk(folder_root, False):
        for name in files:
            match = pattern.search(name)
            if match:
                Files.append(os.path.join(root, name))
    return Files

def check_call(lstArgs):
    retcode = subprocess.Popen(lstArgs)
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