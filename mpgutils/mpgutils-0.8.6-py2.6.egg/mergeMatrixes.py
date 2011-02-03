#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2009 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage %prog [options]
Merge multiple matrixes of data together.  Each is assume to have the same IDs in their rows - 
the number of IDs can be given if it's more than 1 (and the IDs are tested to be the same).
Those IDs will only appear one time in the resulting output.

EG: 
file 1: ID1 ID2 data1 data2
file 2: ID1 ID2 data3 data4
result: ID1 ID2 data1 data2 data3 data4

"""

from __future__ import division
import optparse
import sys
import string
from mpgutils import utils
import shutil

def handleOneFile(file, outFile):
    shutil.copyfile(file.name, outFile)
    return True

def mergeFiles (lstFiles, outFile, numColumns=1):
    lstFileHandles=[open(f, 'r') for f in lstFiles]
    if len(lstFileHandles)==1:
        return handleOneFile(lstFileHandles[0], outFile)
        
    startHandle=lstFileHandles[1]
    out = open (outFile, "w")
    
    #numColumns=numColumns-1
    
    successFlag=True
    while startHandle:
        
        lines=[f.readline() for f in lstFileHandles]
        data=lines[0].split()
        
        if len(data)==0: break;  #hit the end of the data.
        
        lstIDs=data[0:numColumns]            
        
        otherLines=lines[1:]
        otherLines=[l.split() for l in otherLines]
        
        for line in otherLines:
            lstOtherIDs=line[0:numColumns]
            for i in xrange(len(lstIDs)):
                if lstIDs[i]!= lstOtherIDs[i]:
                    print ("Line of first file and subsequent file don't match:" + "original[" + id + "] new [" + o +"]")
                    successFlag=False
        
        otherIDs=[l[0:numColumns] for l in otherLines]
            
        otherLines=[l[numColumns:] for l in otherLines]
        
        for l in otherLines: data.extend(l)
        data.append("\n")
        finalLine = "\t".join(data)
        out.write(finalLine)
        
    out.close()    
    return (successFlag)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", default=None,
                      help="""(Required) Output a single calls or confs file that 
                      is the result of merging multiple calls/confs files""")
    parser.add_option("-n", "--num_columns", default=1, dest="numCols", 
                      help="The number of columns shared between the files, that should match as an identity")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=["output"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    lstFiles = lstArgs[1:len(lstArgs)]
    successFlag=mergeFiles(lstFiles, dctOptions.output, int (dctOptions.numCols))
    if successFlag: print ("Finished Merge Successfully")
    
if __name__ == "__main__":
    sys.exit(main())
    
