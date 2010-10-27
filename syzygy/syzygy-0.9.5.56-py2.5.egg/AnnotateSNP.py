#!/usr/bin/python

import sys
import re
import httplib
import urllib2
import urllib

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
    parser.add_option("--hg")
    parser.add_option("--pif")
    parser.add_option("--tgf")
    parser.add_option("--samtoolspath")
    parser.add_option("--ref")
    parser.add_option("--ncpu")
    parser.add_option("--dbsnp")
    parser.add_option("--bqthr")
    parser.add_option("--skipannot")
    parser.add_option("--chr")
    parser.add_option("--sndb")
    parser.add_option("--module")
    parser.add_option("--infile",
                      default = "snplist.alleles.readyannot")
    parser.add_option("--outputdir")
    parser.add_option("--outfile",
                      default = "snps.annotation.full.1")
    (options, args) = parser.parse_args()

    set_default_mode(BASIC_CONVERSION)

    server = "dirseq"
    port   = "8080"
    path   = "/reseq/ws/reseq/candidate/annotate_candidates"

    includeref = "true"
    filename = options.infile
    username = 'curly'
    password = 'curly'

    call_data = open(os.path.join(options.outputdir,filename), 'r').read() 
    pathout = os.path.join(options.outputdir,str(options.outfile))
    writeannot = open(pathout,'w+')
    url = ''.join(["http://",  server,  ":", port, path])

    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)

    auth_handler = urllib2.HTTPBasicAuthHandler(passman)

    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

    data_dict = {'candidate_data': call_data, 'include_reference_alleles':includeref}
   # print data_dict
    req = urllib2.Request(url, urllib.urlencode(data_dict))

    try:
        r = urllib2.urlopen(req)
        print r
    except IOError, e:
        if e.code == 401:
            sys.stderr.write("Authentication Error!!\n")
            sys.exit()
        else:
            print e.read()
            sys.exit()


    for entry in r:
        writeannot.write(entry)


if __name__ == "__main__":
    main()

