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
Make a guide file from a cel_map file mapping a cel file to a sample name,
and a  list of celFiles in a calls file.
"""

from __future__ import division
import optparse
import sys
import shutil
from mpgutils import utils
import os, re

def main(argv=None):
    if argv is None:
        argv = sys.argv
    lstRequiredOptions=["plateroot"]
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-p", "--plateroot",
                      help="""(Required) Contains folders with larry-bird style files""")
    parser.add_option("-o", "--outputname", default="Output",
                      help="define the file name root for the output files")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    #VALIDATE PATHS
    lstOptionsToCheck = ['plateroot']
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    #OUTPUT FILES
    call_output = os.path.join(dctOptions.plateroot, dctOptions.outputname + ".merged.fawkes.calls")
    conf_output = os.path.join(dctOptions.plateroot, dctOptions.outputname + ".merged.fawkes.confs")
    
    #MERGE FILES
    pattern = re.compile('[.]larry_bird_calls', re.IGNORECASE)
    CallsPaths = utils.findFiles(dctOptions.plateroot, pattern)
    pattern = re.compile('[.]larry_bird_confs', re.IGNORECASE)
    ConfsPaths = utils.findFiles(dctOptions.plateroot,pattern)
    
    #CALLS AND CONFIDENCES
    if len(CallsPaths) != len(ConfsPaths):
        print "The number of Confidence Files and Calls files are not equal"
        print "Calls Files =" + str(CallsPaths)
        print "Confs Files =" + str(ConfsPaths)
        sys.exit(1)
    else:
        if len(CallsPaths) > 1:
            successFlag=utils.mergeFiles(CallsPaths, call_output)
            if not successFlag:
                print "\tCalls Merge Failed"
                sys.exit(2)
                
            #MERGE CONFIDENCES
            successFlag=utils.mergeFiles(ConfsPaths, conf_output)
            if not successFlag:
                print "\tConfs Merge Failed"
                sys.exit(2)
        else:
            if len(CallsPaths) == 1:
                print "\tThere was only one file found, no merge required."
                print "\tCopying calls file to " + call_output
                shutil.copy(CallsPaths[0], call_output)
                print "\tCopying confidence file to " + conf_output
                shutil.copy(ConfsPaths[0], conf_output)

    print "Finished -- Fawkes_Merge.Py\n"
    
if __name__ == "__main__":
    sys.exit(main())
    
