#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2006 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""%prog [-o outputfile -m metaDataFile -s sampleMap] <allele_summary>

Read the allele summary file as produced by cel2cn_allele.py, and write a sanger format intensity file.
"""
from __future__ import division
import optparse
import sys

iPROBESET_ID_FIELD = 0
iCHROMOSOME_FIELD = 1
iPOSITION_FIELD = 2
iPROBESET_TYPE_FIELD = 3
iFIRST_INTENSITY_FIELD = 4

def readMetaData (metaDataFile):
    fIn = open(metaDataFile)
    dctMetaData={}
    for strLine in fIn:
        lstFields=strLine.split()
        snpAName=lstFields[0]
        dctMetaData[snpAName]=lstFields
    return dctMetaData    

def readSampleMap (sampleMapFile):
    fIn = open(sampleMapFile)
    dctSampleMap={}
    for strLine in fIn:
        lstFields=strLine.split()
        celName=lstFields[0]+".CEL"
        sampleName=lstFields[1]
        dctSampleMap[celName]=sampleName
    return dctSampleMap    

def getHeader(strLine, dctSampleMap):
    """Returns the header line, and the index of the fields in the data that should be retained"""
    idx=[]
    lstFields=strLine.split()
    #the first 4 fields stay intact.
    lstResults=lstFields[:iFIRST_INTENSITY_FIELD]
    #change name from probeset type to allele
    lstResults[iPROBESET_TYPE_FIELD]="allele"
    for i in xrange(iFIRST_INTENSITY_FIELD, len(lstFields)):
        field = lstFields[i]
        if field in dctSampleMap:
            idx.append(i);
            naName=dctSampleMap.get(field)
            lstResults.append(naName +"_A")
            lstResults.append(naName +"_B")
    strHeader="\t".join(lstResults) + "\n"
    return strHeader, idx
        
def getSNPLine(strALine, strBLine, dctMetaData, index):
    lstAFields = strALine.split()
    lstBFields = strBLine.split()
    if lstAFields[iCHROMOSOME_FIELD] != lstBFields[iCHROMOSOME_FIELD] or \
       lstAFields[iPOSITION_FIELD] != lstBFields[iPOSITION_FIELD] or \
       len(lstAFields) != len(lstBFields):
        raise Exception("A and B allele lines do not match: " + strALine + strBLine)
    if not lstAFields[iPROBESET_ID_FIELD].endswith("-A"):
        raise Exception("A allele line has strange probeset id: " + strALine)
    if not lstBFields[iPROBESET_ID_FIELD].endswith("-B"):
        raise Exception("B allele line has strange probeset id: " + strBLine)
    # Strip off -A or -B
    lstAFields[iPROBESET_ID_FIELD] = lstAFields[iPROBESET_ID_FIELD][:-2]
    if lstAFields[iPROBESET_ID_FIELD] != lstBFields[iPROBESET_ID_FIELD][:-2]:
        raise Exception("A and B allele lines do not match: " + strALine + strBLine)
    
    
    lstRecord=dctMetaData[lstAFields[iPROBESET_ID_FIELD]]
    lstResult=lstRecord[1:]
    for i in index:
        lstResult.append(lstAFields[i])
        lstResult.append(lstBFields[i])
    strResult="\t".join(lstResult) + "\n"
    return strResult
    
    
def getCNPLine (strLine, dctMetaData, index):
    lstFields = strLine.split()
    lstResult=lstFields[iPROBESET_ID_FIELD:iFIRST_INTENSITY_FIELD]
    lstResult[iPROBESET_TYPE_FIELD]="NN"
    for i in index:
        lstResult.append(lstFields[i])
        lstResult.append("0")
    strResult="\t".join(lstResult) + "\n"
    return strResult
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", dest="output",
                      help="""Where to write output.  Default: stdout""")
    
    parser.add_option("-m", "--metaData", dest="metaData",
                      help="""The SNP meta data File""")
    
    parser.add_option("-s", "--sampleMap", dest="sampleMap",
                      help="""The sample map file""")
    
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) == 1:
        print >> sys.stderr, "ERROR: allele summary file not specified.\n"
        parser.print_help()
        return 1

    if len(lstArgs) > 2:
        print >> sys.stderr, "ERROR: Too many files on command line.\n"
        parser.print_help()
        return 1

    fIn = open(lstArgs[1])

    if dctOptions.metaData is None:
        print >> sys.stderr, "ERROR: Need to supply a meta data file for SNP info.\n"
        parser.print_help()
        return 1
    
    if dctOptions.sampleMap is None:
        print >> sys.stderr, "ERROR: Need to supply a sample map file.\n"
        parser.print_help()
        return 1
    
    if dctOptions.output is None:
        print >> sys.stderr, "ERROR: Need to supply an output Name.\n"
        parser.print_help()
        return 1

    else:
        fOut = sys.stdout

    dctMetaData=readMetaData(dctOptions.metaData)
    dctSampleMap=readSampleMap(dctOptions.sampleMap)
    
    strLastChr=-1
    
    strALine = None
    for strLine in fIn:
            
        if strLine.startswith("probeset_id"):
            strHeader, index = getHeader(strLine, dctSampleMap)
            
    
        elif strLine.startswith("#")==False:
            lstFields = strLine.split("\t", 4)
            currentChr=lstFields[iCHROMOSOME_FIELD]
            #partition output by chromosome
            if currentChr!=strLastChr:
                strLastChr=currentChr
                fOut = open(dctOptions.output+"_chr"+currentChr+".dat","w")
                fOut.write(strHeader)
                
            if lstFields[iPROBESET_TYPE_FIELD] == "C":
                result=getCNPLine(strLine, dctMetaData, index)
                fOut.write(result)
            elif lstFields[iPROBESET_TYPE_FIELD] == "A":
                strALine = strLine
            else:
                if lstFields[iPROBESET_TYPE_FIELD] != "B":
                    raise Exception("Strange value in probeset_type column for line: " + strLine)
                fOut.write(getSNPLine(strALine, strLine, dctMetaData, index))
                strALine = None

    if strALine is not None:
        raise Exception("File ends with A allele line.")
    
    fOut.close()
    

if __name__ == "__main__":
    sys.exit(main())
    
