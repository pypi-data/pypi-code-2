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
import string
from mpgutils import utils

lstRequiredOptions=["pedigree", "output", "celMap"]

def getCelsForCallsFile(callFile):
    """Parse the calls or confidence file, returning the list of cel names"""
    fIn = open(callFile, 'rU')
    line = fIn.readline()
    s=line.split()
    lstCells=s[1:]
    fIn.close()
    return (lstCells)

def getCelMap (celMapFile):
    """Parse a file that has the cel name in col 1, and the sample name in col 2, and return a dictionary."""
    fIn = open(celMapFile, 'rU')
    
    lstTmp=[]
    for strLine in fIn:
         s= strLine.split()
         lstTmp.append(s)
    
    dctCelSample=dict(lstTmp)
    fIn.close()
    return (dctCelSample)

def buildGuideFile(celList, dctCelSample, outFile):
    fOut=open (outFile, "w")
    for c in celList:
        try:
            s=dctCelSample[c]
        except KeyError:
            print "Cel file " + c + " had no entry in celMap"
            s=None
        fOut.write(s+"\n")
    fOut.close()
            
    return (None)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--celMap", default=None,
                      help="""(Required) File with two columns in tab seperated format:
                      CEL_NAME and SAMPLE_NAME.  This file maps one or more cel names to a sample name.""")
    parser.add_option("-c", "--calls", default=None, 
                      help="""(option) A calls or confidence file in traditional apt-probeset-genotype format.""")
    parser.add_option("-o", "--output", default=None,
                      help="""(Required) Output calls file in tped (transposed ped) format""")

    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=["calls", "celMap", "output"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    
    celList=getCelsForCallsFile(dctOptions.calls)
    dctCelSample=getCelMap(dctOptions.celMap)    
      
    buildGuideFile (celList, dctCelSample, dctOptions.output)
    
          
if __name__ == "__main__":
    sys.exit(main())
    
