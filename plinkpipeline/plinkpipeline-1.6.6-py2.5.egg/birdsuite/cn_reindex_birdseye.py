'''
Created on Jun 8, 2010

@author: nemesh
'''

from __future__ import division
import copy
import fileinput
import math
import optparse
import os
import sys
import subprocess
import shutil

from mpgutils import utils

def getCanarySampleIndex(canary_calls):
     fIn = open(canary_calls)
     strHeader = fIn.readline()
     lstFields = strHeader.split()
     lstFields=lstFields[1:]
     count=1
     dctResult={}
     for f in lstFields:
         dctResult[f]=count;
         count=count+1;
     
     return (dctResult)

def rewriteBirdseyeIndex(dctSampleIdx, input_birdseye_calls, output):
    fIn = open(input_birdseye_calls, 'r')
    fOut=open (output, 'w')
    strHeader = fIn.readline()
    #fOut.write(strHeader)
    
    for strLine in fIn:
        lstFields=strLine.split()
        sample=lstFields[0]
        if sample not in dctSampleIdx:
            raise LookupError("Birdseye has sample " + str(sample) + ", but that sample isn't in the canary file!")
        index=dctSampleIdx[sample]
        lstFields[1]=index
        strOut="\t".join([str(val) for val in lstFields])+"\n"
        fOut.write(strOut)
    
    fIn.close()
    fOut.close()
    return (strHeader)
    
def generateFinalIndexedFile(reindexedTempFile, outFile, strHeader):  
    """Sort the output, put the header back on."""
    temp2=reindexedTempFile+ ".sorted"
    
    strCall="sort --key=4n --key=2n --key=5n --key=6n " + reindexedTempFile +" > " + temp2 
    subprocess.Popen(strCall, shell=True).wait()  
    
    fOut=open(outFile, 'w')
    fOut.write(strHeader)
    shutil.copyfileobj(open(temp2,'r'), fOut)
    fOut.close()
    
    #CLEANUP TEMP FILES
    os.remove(temp2)
    os.remove(reindexedTempFile)

    
def reindexBirdseye(canary_calls, input_birdseye_calls, output):
    dctSampleIdx=getCanarySampleIndex(canary_calls)
    reindexedTempFile=output+".temp"
    strHeader=rewriteBirdseyeIndex(dctSampleIdx, input_birdseye_calls, reindexedTempFile)
    generateFinalIndexedFile(reindexedTempFile, output, strHeader)
    

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("--canary_calls", 
                      help="""(Required)  Canary calls file.""")
        
    parser.add_option("--input_birdseye_calls", 
                      help="""(Optional) The matrix of birdseye calls (often produced by post_birdseye --birdseye_calls). """)
                      
    parser.add_option("-o", "--output",
                      help="""(Required) Output file. A reindexed birdseye file, with the samples in the same index order as the canary calls.""")
    
    lstRequiredOptions=['canary_calls', 'input_birdseye_calls', 'output']
    
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    reindexBirdseye(dctOptions.canary_calls, dctOptions.input_birdseye_calls, dctOptions.output)
    
    
if __name__ == "__main__":
    sys.exit(main())
    