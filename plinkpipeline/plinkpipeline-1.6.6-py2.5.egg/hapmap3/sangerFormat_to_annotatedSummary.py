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
"""%prog [-o outputfile ] <sanger format intensity data>

Read the sanger format intensity files as produced by extract_intensity_sanger_format (or by sanger themselves),
and create our default annotated summary format.  This has the ability to concatonate a number of files that span 
chromosomes.
"""

from __future__ import division
import optparse
import sys
from copy import deepcopy
from mpgutils.fk_utils import arbslice
from mpgutils import fk_utils

iPROBESET_ID_FIELD = 0
iCHROMOSOME_FIELD = 1
iPOSITION_FIELD = 2
iALLELE_FIELD = 3
iFIRST_INTENSITY_FIELD = 4
MISSING_VALUE_LABEL=str (-9999)

def splitIntoAlleleFields(strLine):
    """Splits line into A and B lines.  Returns the info fields (probeset, chr, etc),
    the A probe fields, and the B probe fields."""
    lstFields=strLine.split()
    fieldAIndex=range(iFIRST_INTENSITY_FIELD, len(lstFields),2)
    fieldBIndex=range(iFIRST_INTENSITY_FIELD+1, len(lstFields),2)
    lstAFields = arbslice (lstFields, fieldAIndex)
    lstBFields = arbslice (lstFields, fieldBIndex)
    infoFields=lstFields[:iFIRST_INTENSITY_FIELD]
    return (infoFields, lstAFields, lstBFields)
        
def getHeader(strLine):
    """Returns the header line"""
    infoFields, lstAFields, lstBFields = splitIntoAlleleFields(strLine)
    infoFields[iPROBESET_ID_FIELD]='probeset_id'
    infoFields[iCHROMOSOME_FIELD]='chr'
    infoFields[iALLELE_FIELD]='probeset_type'
    
    #Strip off the _A or _B
    lstFields = [x[:-2] for x in lstAFields]
    lstResult=[]
    lstResult.extend(infoFields)
    lstResult.extend(lstFields)
    strHeader="\t".join(lstResult) + "\n"
    return strHeader

def getLine(strLine, probeAllele, intensityMultiplier, missingValueLabel):
    """Convert 1 line that has A and B intensity info into one lines of output, 
    either the A or B probe depending on which probe allele is requested."""

    setValidProbeAlleles=set (['A', 'B'])
    if probeAllele not in setValidProbeAlleles:
        print >> sys.stderr, "ERROR: You can't use probe allele " + probeAllele
        return 1
    
    infoFields, lstAFields, lstBFields = splitIntoAlleleFields(strLine)
                           
    #if (infoFields[iALLELE_FIELD])=="NN":
    #    infoFields[iALLELE_FIELD]="C"
    #else:
    
    infoFields[iALLELE_FIELD]=probeAllele
        
    infoFields[iPROBESET_ID_FIELD]=infoFields[iPROBESET_ID_FIELD]+("-"+probeAllele)
    
    lstResult=[]
    lstResult.extend(infoFields)
    if (probeAllele=="A"):
        
        lstAFields=modifyIntensitySpace(lstAFields, intensityMultiplier, missingValueLabel)
        lstResult.extend(lstAFields)
    else:
        lstBFields=modifyIntensitySpace(lstBFields, intensityMultiplier, missingValueLabel)
        lstResult.extend(lstBFields)
    
    strResult="\t".join(lstResult) + "\n"
    return strResult
    
def modifyIntensitySpace (lstIntensity, intensityMultiplier, missingValueLabel):
    
    #find missing values and change them to cannonical labels
    strRow=[str(x) for x in lstIntensity]
    #don't use this index until you've already mutliplied, or you'll multiply your label!
    idxMissingVals=fk_utils.indices(strRow, str (missingValueLabel))
    
    #multiply intensity space for all values.
    result=[float(x) * intensityMultiplier for x in lstIntensity]
    
    #convert back to strings.
    result=[str(x) for x in result]
    
    #put it missing values.
    if len(idxMissingVals)>0:
        for i in idxMissingVals:
            result[i]=MISSING_VALUE_LABEL

    return result

def processFile (strFile, fOut, intensityMultiplier, missingValueLabel, boolWriteHeader):
    fIn = open(strFile)
    strLine = None
    for strLine in fIn:
            
        if strLine.startswith("probe_name") or strLine.startswith("probeset_id"):
            strHeader=getHeader(strLine)
            if (boolWriteHeader):
                fOut.write(strHeader)
            
        elif strLine.startswith("#")==False:
            
            strAResult=getLine(strLine, "A", intensityMultiplier, missingValueLabel)
            strBResult=getLine(strLine, "B", intensityMultiplier, missingValueLabel)
            fOut.write(strAResult)
            fOut.write(strBResult)
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", dest="output",
                      help="""Where to write output.  Default: stdout""")
    
    parser.add_option("-i", "--intensity_multiplier", dest="intensityMultiplier", default=1,
                      help="""What to multiply intensity by to make it similar to other data sets. 
                      Defaults to 1 (no change)""")
    
    parser.add_option("-m", "--missing_value_label", dest="missingValueLabel", default="-9999",
                      help="""Encode this value in the canonical missing value label (-9999)""")
        
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) == 1:
        print >> sys.stderr, "ERROR: at least one intensity file must be specified.\n"
        parser.print_help()
        return 1
    
    if dctOptions.output is not None:
        fOut = open(dctOptions.output, "w")
    else:
        fOut = sys.stdout
    
    intensityMultiplier=float (dctOptions.intensityMultiplier)
    missingValueLabel=dctOptions.missingValueLabel
    
    for i in xrange(1,len (lstArgs)):
        strFile=lstArgs[i]
        if (i==1):
            processFile(strFile, fOut, intensityMultiplier, missingValueLabel, True)
        else:
            processFile (strFile, fOut, intensityMultiplier, missingValueLabel, False)
        
    fOut.close()
    

if __name__ == "__main__":
    sys.exit(main())
    
