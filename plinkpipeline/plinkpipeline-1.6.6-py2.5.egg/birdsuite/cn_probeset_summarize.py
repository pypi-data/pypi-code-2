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
"""%prog [options] summaries-files...

Summarize groups of probesets that are within the range of known CNPs.
Requires at least one summaries file, which is a tab-separated input file with allele or locus probe summaries,
ordered by genomic position.

"""
from __future__ import division
import optparse
import sys

import numpy
import medpolish
from mpgutils import utils
from numpy import median
from numpy import any
from mpgutils import fk_utils

# Definitions of columns in CNP definition file
NUM_CNP_DEFINITION_FIELDS = 5
CNP_DEF_CNP_ID_FIELD_INDEX = 0
CNP_DEF_CHR_FIELD_INDEX = 1
CNP_DEF_START_POSN_FIELD_INDEX = 2
CNP_DEF_END_POSN_FIELD_INDEX = 3
CNP_DEF_NUM_PROBES_FIELD_INDEX = 4
CNP_DEF_FIRST_INT_FIELD = CNP_DEF_START_POSN_FIELD_INDEX
CNP_DEF_LAST_INT_FIELD = 4

# Definitions of columns in smart probeset CNP definition file
NUM_SMART_CNP_DEFINITION_FIELDS = 3
SMART_CNP_DEF_CNP_ID_FIELD_INDEX = 0
SMART_CNP_DEF_CHR_FIELD_INDEX = 1
SMART_CNP_DEF_POSN_FIELD_INDEX = 2

# Definitions of columns in build-independend smart probeset CNP definition file
NUM_BI_SMART_CNP_DEFINITION_FIELDS = 2
BI_SMART_CNP_DEF_CNP_ID_FIELD_INDEX = 0
BI_SMART_CNP_DEF_PROBE_ID_FIELD_INDEX = 1

# Definitions of columns in the input summary file
# The index of the first intensity in the input summary file
SUMMARY_FIRST_INTENSITY_FIELD_INDEX=4
SUMMARY_PROBE_FIELD_INDEX=0
SUMMARY_CHR_FIELD_INDEX=1
SUMMARY_POSN_FIELD_INDEX=2
SUMMARY_PROBESET_TYPE_FIELD_INDEX=3

#CHANGE TO nan

MISSING_VALUE_LABEL=float('nan')

def indexNaN(x):
    y=[]
    for k in range (len(x)):
        if (numpy.isnan(x[k])):
            y.append(k)
    return (y) 


def npmedian (x):
    """Dear numPY.  Please don't change your APIs, so I don't have to wrap them."""
    nv=numpy.__version__
    
    if (nv =="1.0.1" or nv =="1.0.4" or nv=="1.1" or nv =="1.1.1"): 
        return median(x)
    
    return median(x, axis=0)

def cmpCNPDefinitionsByName(a, b):
    """Sorts CNPs by name, doing numeric sort if possible"""
    if a.strCNPId.isdigit() and b.strCNPId.isdigit():
        return cmp(int(a.strCNPId), int(b.strCNPId))
    if a.strCNPId.isdigit():
        return -1
    if b.strCNPId.isdigit():
        return 1
    return cmp(a.strCNPId, b.strCNPId)

def cmpCNPAndAccumulatedIntensitiesTupByName(a, b):
    return cmpCNPDefinitionsByName(a[0], b[0])

def cmpCNPDefinitionsByPosition(a, b):
    """Sorts CNPs by locus.  Primary sort is chromosome, then end posn, then start posn"""
    iCmpChromosome = cmp(a.iChr, b.iChr)
    if iCmpChromosome != 0:
        return iCmpChromosome
    iCmpEndPosn = cmp(a.iEndPosn, b.iEndPosn)
    if iCmpEndPosn != 0:
        return iCmpEndPosn

    return cmp(a.iStartPosn, b.iStartPosn)


class RangeCNP(object):
    """Holds the definition of a CNP that is described by start and end loci."""
    def __init__(self, strLine):
        lstFields = strLine.split()
        # Allow last field to be absent
        if len(lstFields) < NUM_CNP_DEFINITION_FIELDS - 1 or \
               len(lstFields) > NUM_CNP_DEFINITION_FIELDS:
            raise Exception("Wrong number of fields (%d) in %s.  Expected %d fields." % \
                            (len(lstFields), strCnpDefsFile, NUM_CNP_DEFINITION_FIELDS))

        self.strCNPId = lstFields[CNP_DEF_CNP_ID_FIELD_INDEX]
        self.iChr = int(utils.convertChromosomeStr(lstFields[CNP_DEF_CHR_FIELD_INDEX]))
        self.iStartPosn = int(lstFields[CNP_DEF_START_POSN_FIELD_INDEX])
        self.iEndPosn = int(lstFields[CNP_DEF_END_POSN_FIELD_INDEX])
        if len(lstFields) > CNP_DEF_NUM_PROBES_FIELD_INDEX:
            self.iNumProbes = int(lstFields[CNP_DEF_NUM_PROBES_FIELD_INDEX])
        else: self.iNumProbes = None

    def hasPosition(self):
        "This CNP is defined by positions, rather than probe names"
        return True
    
    def getOutputFields(self):
        return [self.strCNPId, str(self.iChr), str(self.iStartPosn), str(self.iEndPosn)]


    def cmpToProbeSet(self, lstFields):
        """Returns -1 if probe set is after cnp, +1 if probeset is before cnp, 0 if within cnp.""" 
        iCmp = cmp(self.iChr, lstFields[SUMMARY_CHR_FIELD_INDEX])
        if iCmp != 0:
            return iCmp

        iPosition = lstFields[SUMMARY_POSN_FIELD_INDEX]
        if iPosition < self.iStartPosn:
            return 1
        if iPosition > self.iEndPosn:
            return -1
        return 0

    def __str__(self):
        return str(self.getOutputFields())

class SmartCNP(object):
    """Holds the definition of a CNP that is described by a list of loci."""
    def getSmartCNPId(strLine):
        '''Static method that returns the ID of the SmartCNP, so that it can be decided
        whether to create a new one or to add to an old one.'''
        return SmartCNP._splitSmartCNPList(strLine)[SMART_CNP_DEF_CNP_ID_FIELD_INDEX]

    getSmartCNPId = staticmethod(getSmartCNPId)

    def _splitSmartCNPList(strLine):
        lstFields = strLine.split()
        if len(lstFields) != NUM_SMART_CNP_DEFINITION_FIELDS:
            raise Exception("Wrong number of fields (%d) in smart probeset file.  Expected %d fields." % \
                            (len(lstFields), NUM_SMART_CNP_DEFINITION_FIELDS))
        return lstFields

    _splitSmartCNPList = staticmethod(_splitSmartCNPList)
    
    def __init__(self, strCNPId):
        self.strCNPId = strCNPId;
        self.iChr = None
        self.iStartPosn = None
        self.iEndPosn = None
        self.lstPositions = []
        self.iNumProbes = None
        
    def hasPosition(self):
        "This CNP is defined by positions, rather than probe names"
        return True
    
    def addPosition(self, strLine):
        lstFields = self._splitSmartCNPList(strLine)
            
        strCNPId = lstFields[SMART_CNP_DEF_CNP_ID_FIELD_INDEX]
        iChr = int(utils.convertChromosomeStr(lstFields[SMART_CNP_DEF_CHR_FIELD_INDEX]))
        iPosn = int(lstFields[SMART_CNP_DEF_POSN_FIELD_INDEX])
        assert(strCNPId == self.strCNPId)
        if self.iChr is None:
            self.iChr = iChr
        elif iChr != self.iChr:
            raise Exception("Multiple chromosomes for same CNP definition: " + strCNPId)
        if iPosn in self.lstPositions:
            raise Exception("Duplicated line in SmartCNP definitions: " + strLine)
        self.lstPositions.append(iPosn)
        if self.iStartPosn is None:
            self.iStartPosn = iPosn
        if self.iEndPosn is None:
            self.iEndPosn = iPosn
        self.iStartPosn = min(self.iStartPosn, iPosn)
        self.iEndPosn = max(self.iEndPosn, iPosn)

    def getOutputFields(self):
        return [self.strCNPId, str(self.iChr), str(self.iStartPosn), str(self.iEndPosn)]

    def cmpToProbeSet(self, lstFields):
        """Returns -1 if probe set is after cnp, +1 if probeset is before cnp, 0 if within cnp.""" 
        iCmp = cmp(self.iChr, lstFields[SUMMARY_CHR_FIELD_INDEX])
        if iCmp != 0:
            return iCmp

        iPosition = lstFields[SUMMARY_POSN_FIELD_INDEX]
        if iPosition < self.iStartPosn:
            return 1
        if iPosition > self.iEndPosn:
            return -1
        if iPosition in self.lstPositions:
            return 0
        return None

    def __str__(self):
        return str(self.getOutputFields())

    
class BISmartCNP(object):
    """Holds the definition of a CNP that is described by a list of probe names, aka a build-independent smart CNP."""
    def getSmartCNPId(strLine):
        '''Static method that returns the ID of the SmartCNP, so that it can be decided
        whether to create a new one or to add to an old one.'''
        return BISmartCNP._splitSmartCNPList(strLine)[BI_SMART_CNP_DEF_CNP_ID_FIELD_INDEX]

    getSmartCNPId = staticmethod(getSmartCNPId)

    def _splitSmartCNPList(strLine):
        lstFields = strLine.split()
        if len(lstFields) != NUM_BI_SMART_CNP_DEFINITION_FIELDS:
            raise Exception("Wrong number of fields (%d) in smart probeset file.  Expected %d fields." % \
                            (len(lstFields), NUM_BI_SMART_CNP_DEFINITION_FIELDS))
        return lstFields

    _splitSmartCNPList = staticmethod(_splitSmartCNPList)
    
    def __init__(self, strCNPId):
        self.strCNPId = strCNPId;
        self.stProbes = set()
        self.iChr = None
        self.iStartPosn = None
        self.iEndPosn = None
        self.iNumProbes = None
        
    def hasPosition(self):
        "This CNP is defined by probe names, rather than positions"
        return False
    
    def addProbe(self, strLine):
        lstFields = self._splitSmartCNPList(strLine)
            
        strCNPId = lstFields[BI_SMART_CNP_DEF_CNP_ID_FIELD_INDEX]
        strProbe = lstFields[BI_SMART_CNP_DEF_PROBE_ID_FIELD_INDEX]
        assert(strCNPId == self.strCNPId)
        self.stProbes.add(strProbe)

    def _addPosition(self, lstFields):
        """Add position info to a BI smart CNP definition from locus summary file."""
        iChr = int(utils.convertChromosomeStr(lstFields[SUMMARY_CHR_FIELD_INDEX]))
        iPosn = int(lstFields[SUMMARY_POSN_FIELD_INDEX])
        if self.iChr is None:
            self.iChr = iChr

        # if a probe is on a different chromosome than the first probe, ignore it for the purpose
        # of computing range
        if iChr == self.iChr:
            if self.iStartPosn is None:
                self.iStartPosn = iPosn
            if self.iEndPosn is None:
                self.iEndPosn = iPosn
            self.iStartPosn = min(self.iStartPosn, iPosn)
            self.iEndPosn = max(self.iEndPosn, iPosn)

    def getOutputFields(self):
        return [self.strCNPId, str(self.iChr), str(self.iStartPosn), str(self.iEndPosn)]

    def cmpToProbeSet(self, lstFields):
        """Returns -1 if probe set is after cnp, +1 if probeset is before cnp, 0 if within cnp."""
        if lstFields[SUMMARY_PROBE_FIELD_INDEX] in self.stProbes:
            self._addPosition(lstFields)
            return 0
        else: -1

    def __str__(self):
        return str(self.getOutputFields())

    

def loadRangeCNPDefinitions(strCnpDefsFile):
    """Reads the CNP definitions from the file, does some validation, sorts by genomic positions,
    and returns a list of RangeCNP objects."""
    
    lstRet = []
    fIn = open(strCnpDefsFile)
    strHeader = fIn.readline()
    lstFields = strHeader.split()
    # Skip header line
    if lstFields[0] != "cnp_id":
        raise Exception("Header missing from CNP definition file " + strCnpDefsFile  +
                        ".  Expected header line 'cnp_id chr start end'.")
    
    for strLine in fIn:
        lstRet.append(RangeCNP(strLine))

    fIn.close()

    return lstRet

def loadSmartCNPDefinitions(strSmartCnpDefsFile):
    """Reads the CNP definitions from the file, does some validation, sorts by genomic positions,
    and returns a list of ListCNP objects."""
    
    fIn = open(strSmartCnpDefsFile)
    strHeader = fIn.readline()
    lstFields = strHeader.split()
    # Skip header line
    if lstFields[0] != "cnp_id":
        raise Exception("Header missing from CNP definition file " + strSmartCnpDefsFile  +
                        ".  Expected header line 'cnp_id chr pos'.")

    dctCNPs = {}
    
    for strLine in fIn:
        strCNPId = SmartCNP.getSmartCNPId(strLine)
        if strCNPId in dctCNPs:
            smartCNP = dctCNPs[strCNPId]
        else:
            smartCNP = SmartCNP(strCNPId)
            dctCNPs[strCNPId] = smartCNP
        smartCNP.addPosition(strLine)

    fIn.close()

    return dctCNPs.values()

def loadBISmartCNPDefinitions(strCnpDefsFile):
    fIn = open(strCnpDefsFile)
    strHeader = fIn.readline()
    lstFields = strHeader.split()
    # Skip header line
    if lstFields[0] != "cnp_id":
        raise Exception("Header missing from CNP definition file " + strCnpDefsFile  +
                        ".  Expected header line 'cnp_id probeset_id'.")
    dctCNPs = {}
    
    for strLine in fIn:
        strCNPId = BISmartCNP.getSmartCNPId(strLine)
        if strCNPId in dctCNPs:
            smartCNP = dctCNPs[strCNPId]
        else:
            smartCNP = BISmartCNP(strCNPId)
            dctCNPs[strCNPId] = smartCNP
        smartCNP.addProbe(strLine)

    fIn.close()

    return dctCNPs.values()

class LocusCNVAccumulator(object):
    """For accumulating intensities into CNVs that are defined by loci"""
    def __init__(self, lstCNVs):
        lstCNVs = lstCNVs[:]
        lstCNVs.sort(cmpCNPDefinitionsByPosition)
        self._lstCNVsAndAccumulators = [(cnp, []) for cnp in lstCNVs]
        self._lstForIteration = self._lstCNVsAndAccumulators[:]

    def accumulate(self, lstFields):
        # remove from iteration list CNPs that are known to be earlier in position
        while len(self._lstForIteration) > 0 and \
              (self._lstForIteration[0][0].iChr < lstFields[SUMMARY_CHR_FIELD_INDEX] or \
               (self._lstForIteration[0][0].iChr == lstFields[SUMMARY_CHR_FIELD_INDEX] and \
                self._lstForIteration[0][0].iEndPosn < lstFields[SUMMARY_POSN_FIELD_INDEX])):
            del self._lstForIteration[0]

        for cnp, lstRows in self._lstForIteration:
            if cnp.iChr > lstFields[SUMMARY_CHR_FIELD_INDEX]:
               break
            iCmp = cnp.cmpToProbeSet(lstFields)
            if iCmp == 0:
                lstRows.append(lstFields)

    def getCNVsAndAccumlatedIntensities(self):
        """Return a list of tuples(cnv, lstAccumulatedIntensities)"""
        return self._lstCNVsAndAccumulators

class NameCNVAccumulator(object):
    """For accumulating intensities into CNVs that are defined by probe names"""
    def __init__(self, lstCNVs):
        self._dctCNVsByProbe = {}
        self._lstCNVsAndAccumulators = [(cnp, []) for cnp in lstCNVs]

        for tup in self._lstCNVsAndAccumulators:
            cnp = tup[0]
            for strProbe in cnp.stProbes:
                lstCNVsForProbe = self._dctCNVsByProbe.setdefault(strProbe, [])
                lstCNVsForProbe.append(tup)

    def accumulate(self, lstFields):
        try:
            lstTups = self._dctCNVsByProbe[lstFields[SUMMARY_PROBE_FIELD_INDEX]]
            for cnp, lstRows in lstTups:
                # This is done only to record the position
                iCmp = cnp.cmpToProbeSet(lstFields)
                assert(iCmp == 0)
                lstRows.append(lstFields)
        except:
            # probe is not in any CNV
            pass
            
    def getCNVsAndAccumlatedIntensities(self):
        """Return a list of tuples(cnv, lstAccumulatedIntensities)"""
        return self._lstCNVsAndAccumulators


lstSTANDARD_HEADERS=["cnp_id", "chr", "start_position", "end_position"]

def sloshHeader(fOut, fIn, retainAll=True, bNoLocus=False):
    """Read header from input, write to output, adjusting column headers appropriately.
    If retainAll is True, all headers will be retained.  Otherwise, only the header starting with probeset_id will be retained."""
    for strLine in fIn:
        if strLine.startswith("probeset_id"):
            lstInHeaders = strLine.split()
            lstFirstHeaders = lstSTANDARD_HEADERS[:]
            if bNoLocus:
                del lstFirstHeaders[1:]
            lstOutHeaders = lstFirstHeaders + \
                            lstInHeaders[SUMMARY_FIRST_INTENSITY_FIELD_INDEX:]
            print >> fOut, "\t".join(lstOutHeaders)
            break
        else:
            fOut.write(strLine)

def extractIntensitiesFromSummaryFields(lstFields, missingValueLabel):
    """Returns list of floats given string fields of a probe set summary line."""
    intensityFields=lstFields[SUMMARY_FIRST_INTENSITY_FIELD_INDEX:]
    
    missingDataIndex=fk_utils.indices(intensityFields,  missingValueLabel)
    if len(missingDataIndex)>0:
        for i in missingDataIndex: intensityFields[i]=MISSING_VALUE_LABEL
        
    result=[float(strIntensity) for strIntensity in intensityFields]
    return (result)

def median_polish(lstRows, bVerbose=False):
    matIntensities = numpy.array(lstRows)
    #FIX FOR SNP/SAMPLE MISSING, happens with illumina data.
    
    matIntensities=fixZeroIntensities(matIntensities)
    matIntensities=fixMissingIntensites(matIntensities)
    overall, rowEffects, columnEffects, residuals = medpolish.medpolish(matIntensities)
    if bVerbose:
        print >> sys.stderr, "medpolish result for :", matIntensities
        print >> sys.stderr, "\noverall", overall, "\nrowEffects", rowEffects, "\ncolumnEffects", columnEffects, "\bresiduals", residuals
    columnEffects += overall
    return columnEffects

def median_polish_exp(lstRows, bVerbose=False):
    matIntensities = numpy.array(lstRows)
    
    #Fix for illumina data where a sample/SNP combo may be missing in a particular instant.
    #missing data would explode log/median polish
    
    matIntensities=fixZeroIntensities(matIntensities)
    matIntensities=fixMissingIntensites(matIntensities)
    
    logIntensities= numpy.log(matIntensities)
    
    overall, rowEffects, columnEffects, residuals = medpolish.medpolish(numpy.log(matIntensities))
    if bVerbose:
        print >> sys.stderr, "medpolish_exp result for :", matIntensities
        print >> sys.stderr, "\noverall", overall, "\nrowEffects", rowEffects, "\ncolumnEffects", columnEffects, "\bresiduals", residuals
    columnEffects += overall
    return numpy.exp(columnEffects)

def sumProbes(lstRows, bVerbose=False):
    matIntensities = numpy.array(lstRows)
    
    counter=0
    for row in matIntensities:
        
        idx=indexNaN(row)
        if (len(idx)>0):         
            row[idx]=0
            matIntensities[counter]=row
        counter=counter+1
    result=numpy.sum(matIntensities, axis=0)
    return result
    
    
def rescale_median(lstRows, bVerbose=False):
    matIntensities = numpy.array(lstRows)
    # Take mean of each row
    means = matIntensities.mean(axis=1)

    # The result of the above is 1-row matrix rather than a 1-column matrix,
    # so duplicate by number of columns, and then transpose so the mean of
    # each row can be subtracted from the values in each row.
    means = utils.repmat(means, matIntensities.shape[1], 1).transpose()
    matIntensities -= means

    # Transform stDevs the same way means was transformed.
    stDevs = matIntensities.std(axis=1)
    stDevs = utils.repmat(stDevs, matIntensities.shape[1], 1).transpose()

    matIntensities /= stDevs
    return npmedian(matIntensities)
    
class InputFileWithPushBack(object):
    def __init__(self, strPath):
        self.fIn = open(strPath)
        self.strPushedBackLine = None

    def pushLineBack(self, strLine):
        assert(self.strPushedBackLine is None)
        self.strPushedBackLine = strLine
        
    def __iter__(self):
        return (self)

    def next(self):
       if self.strPushedBackLine is not None:
           strRet = self.strPushedBackLine
           self.strPushedBackLine = None
           return (strRet)
       strLine=self.fIn.readline()
       if len(strLine) == 0:
                raise StopIteration
       return (strLine)
       
    def close(self):
        self.fIn.close()

class InputFileMergeWithPushBack (object):
    def __init__(self, strPathList):
        
        self.lstFilesIn = [InputFileWithPushBack(f) for f in strPathList]
        #skip the headers in every file, get to the probeset_ID header.
        for f in self.lstFilesIn:
            for strLine in f:
                if strLine.startswith("probeset_id"): 
                    f.pushLineBack(strLine)
                    break      
                
        self.strPushedBackLine = None
        self.delimiter="\t" #change this to be a parameter
        
    def pushLineBack(self, strLine):
        assert(self.strPushedBackLine is None)
        self.strPushedBackLine = strLine

    #assumption is that the files are all in the same probe order.  
    #Check that the probe identifiers are the same in all the files.
    #If the probe ID in different in any file, give up!
    def __testLinesSame(self, strBaseLine, lstStrOtherLines):
        strJoin=":"
        baseSplit=strBaseLine.split(self.delimiter, 4)
        startID=strJoin.join(baseSplit[:SUMMARY_PROBESET_TYPE_FIELD_INDEX+1])
        lstBaseSplit=[l.split(self.delimiter, 4) for l in lstStrOtherLines]
        strOtherLineIDs=[strJoin.join(l[:SUMMARY_PROBESET_TYPE_FIELD_INDEX+1]) for l in lstBaseSplit]
        for strTest in strOtherLineIDs:
                if strTest!=startID: 
                    strMsg="The summary files are not in frame with each other.  Start ID: " + str(startID) + " other IDs: " +  str(strOtherLineIDs)
                    raise Exception (strMsg)
        return True
    
    def __joinData(self, strBaseLine, lstStrOtherLines):
        #join the probe info from the base line, and the data from the base and other lines together.
        lstData=[strBaseLine]
        lstBaseSplit=[l.split(self.delimiter, 4) for l in lstStrOtherLines]
        lstData.extend([strLine[SUMMARY_FIRST_INTENSITY_FIELD_INDEX] for strLine in lstBaseSplit])
        result=self.delimiter.join(lstData)
        #do I need to strip newlines here?
   
        result = result.replace("\n", "")
       #print (result)
        return (result)
    
    def next (self):
        if self.strPushedBackLine is not None:
           strRet = self.strPushedBackLine
           self.strPushedBackLine = None
           return (strRet)
       
        strLine=self.lstFilesIn[0].next()
        if len(strLine) == 0:
                raise StopIteration         
        strOtherLines=[f.next() for f in self.lstFilesIn[1:]]
        self.__testLinesSame(strLine, strOtherLines)
        result=self.__joinData(strLine, strOtherLines)
          
        return (result)
   
    def __iter__(self):
        return (self)
    
    def close(self):
        [f.close() for f in self.lstFilesIn]
        
dctSUMMARIZATION_ALGORITHMS = {
    "medpolish": median_polish,
    "medpolish-exp": median_polish_exp,
    "rescale-median": rescale_median,
    "sum": sumProbes
    }

strDEFAULT_SUMMARIZATION_ALGORITHM="medpolish-exp"

def loadProbes(strPath):
    "Return a list of the probes in the file"
    fIn = open(strPath)
    try:
        return [strLine.rstrip() for strLine in fIn]
        print ("Normalization probes loaded")
    finally:
        fIn.close()

def findMediansOfSelectProbes(lstProbeSummariesFiles, stProbes, strMissingValueLabel):
    """For each sample in the probe summaries file, extract each probe in stProbes,
    and find the median of probe intensities for that sample.  Return a list of
    medians in the order of the samples in the probe summaries file."""
    print ("Finding probe medians")
    fIn = InputFileMergeWithPushBack(lstProbeSummariesFiles)
    
    for strLine in fIn:
        if strLine.startswith("probeset_id"):
            break
    else:
        raise Exception("Never saw header line in " + strProbeSummariesFile)

    lstMatrix = []
    stFoundProbes = set()
    for strLine in fIn:
        lstFields = strLine.split()
        if lstFields[SUMMARY_PROBE_FIELD_INDEX] not in stProbes:
            continue
        stFoundProbes.add(lstFields[SUMMARY_PROBE_FIELD_INDEX])
        lstMatrix.append(extractIntensitiesFromSummaryFields(lstFields, strMissingValueLabel))

    
    if len(stProbes) != len(lstMatrix):
        raise Exception("Not all normalization probes found in summary file " + str(lstProbeSummariesFiles) +
                        "; " + str(stProbes - stFoundProbes))
    fIn.close()
    
    matIntensities = numpy.array(lstMatrix)
    
    matIntensities=fixZeroIntensities(matIntensities)
    matIntensities=fixMissingIntensites(matIntensities)
    result=npmedian(lstMatrix)
    print ("Probe medians found")
    return result 
    
def fixMissingIntensites (matIntensities):
    """For a matrix of intensity scores, there may be missing scores that are encoded with 
    the missing value constant.  Change these values to the median of the samples."""
    
    rowIdx=0
    maxIdx=len(matIntensities)
    while rowIdx<maxIdx:
        row=matIntensities[rowIdx]
        idx=indexNaN(row)
        if (len(idx)>0):
            remaining=fk_utils.arbNegSlice(row, idx)
            if len(remaining)==0:
                matIntensities=numpy.delete (matIntensities,rowIdx,axis=0)                
                rowIdx=rowIdx-1
                maxIdx=maxIdx-1
                
            else:
                replacement = median(remaining)
                row[idx]=replacement
                matIntensities[rowIdx]=row
        rowIdx=rowIdx+1
        
    return (matIntensities)

def fixZeroIntensities (matIntensities):
    """For a matrix of intensity scores, change all 0 scores to 1."""
    
    counter=0
    for row in matIntensities:
        idx=fk_utils.indices(row, float (0))
        if (len(idx)>0):      
            row[idx]=1
            matIntensities[counter]=row
        counter=counter+1
        
    return (matIntensities)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-c", "--cnps", dest="cnpDefsFile", 
                      help="""Tab-separated input file with the following columns:
CNP ID, chromosome, start genomic position, end genomic position (inclusive).
At least one of --cnps and --smart-cnps must be used.""")
    parser.add_option("--smart-cnps", dest="smartCnpDefsFile", 
                      help="""Tab-separated input file with the following columns:
CNP ID, chromosome, genomic position.  Multiple lines for the same CNP ID are allowed.
At least one of --cnps and --smart-cnps must be used.""")

    parser.add_option("--bi-smart-cnps", dest="biSmartCnpDefsFile", 
                      help="""Build-independent smart probe file.  Tab-separated input file with the following columns:
CNP ID, probeset_id.  Multiple lines for the same CNP ID are allowed.
At least one of --cnps and --smart-cnps must be used.""")


#    parser.add_option("-s", "--summary", dest="probeSummariesFile",
#                      help="""Tab-separated input file with allele or locus probe summaries,
#ordered by genomic position.  Required.""")

    parser.add_option("-o", "--output", dest="output", 
                      help="""Tab-separated output file in tabular format, with one row for each CNP in cnpRangeFile
and one column for each sample in the input probeSummaryFile.  The value in each cell of the table
is the result of median polishing all the intensities for the CNP (i.e. all the probe sets in the CNP,
                      and all the samples.  Default: stdout.""")
    parser.add_option("-a", "--algorithm", dest="summarizationAlgorithm", 
                      choices=dctSUMMARIZATION_ALGORITHMS.keys(), 
                      default=strDEFAULT_SUMMARIZATION_ALGORITHM, 
                      help="""Which summarization algorithm to use.  One of %s  Default: %s.""" %
                      (str(dctSUMMARIZATION_ALGORITHMS.keys()), strDEFAULT_SUMMARIZATION_ALGORITHM))
    parser.add_option("--ignore-snps", dest="ignoreSNPs", default=False, action="store_true", 
                      help="""Skip SNP intensities and just summarize CNP intensities.""")
    parser.add_option("--normalization-probes", dest="normalizationProbes", 
                      help="""Optional list of probes for normalizing each sample.  For each sample,
                      find the median of these probes and divide the output intensity by this value.""")
    parser.add_option("--no_locus", action="store_true", default=False, 
                      help="Do not emit CNP locus information (chromosome, start and stop) in output.")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, 
                      help="Enable debugging output")
    parser.add_option("-m", "--missing_value_label", dest="strMissingValueLabel", default="NaN", 
                      help="""Label of data that is missing from the platform.  
                      Illumina products do not always have data available for every probe/individual combination.
                      Default is %default""")

    dctOptions, lstArgs = parser.parse_args(argv)
    
#    if len(lstArgs) > 1:
#        print >> sys.stderr, "ERROR: Too many arguments on command line.\n"
#        parser.print_help()
#        return 1
    if len(lstArgs) < 2:
        print >> sys.stderr, "ERROR: Missing required arguments.  Requires at least 1 summary file.\n"
        parser.print_help()
        return 1
    
    lstProbeSummariesFiles=lstArgs[1:]
    
    if dctOptions.cnpDefsFile is None and dctOptions.smartCnpDefsFile is None and dctOptions.biSmartCnpDefsFile is None:
        print >> sys.stderr, "ERROR: Missing required arguments.\n"
        parser.print_help()
        return 1


    if dctOptions.strMissingValueLabel is not None:
        #refactor this as a proper parameter.
        #globals()["MISSING_VALUE_LABEL"] =  dctOptions.strMissingValueLabel
        strMissingValueLabel=dctOptions.strMissingValueLabel
        print >> sys.stderr, "Missing Value Label set as " + strMissingValueLabel + "\n"
        
        
    if dctOptions.output is not None:
        fOut = open(dctOptions.output, "w")
    else:
        fOut = sys.stdout

    if dctOptions.cnpDefsFile is not None:
        lstRangeCNPs = loadRangeCNPDefinitions(dctOptions.cnpDefsFile)
    else: lstRangeCNPs = []

    stCNPsSeen = set([cnp.strCNPId for cnp in lstRangeCNPs])

    if dctOptions.smartCnpDefsFile is not None:
        lstSmartCNPs = loadSmartCNPDefinitions(dctOptions.smartCnpDefsFile)
    else: lstSmartCNPs = []

    stNewCNPs = set([cnp.strCNPId for cnp in lstSmartCNPs])
    if len(stCNPsSeen & stNewCNPs) > 0:
        raise Exception("Some CNP definitions in " + dctOptions.smartCnpDefsFile + " overlap a previously-loaded CNP definition")
    stCNPsSeen |= stNewCNPs

    if dctOptions.biSmartCnpDefsFile is not None:
        lstBISmartCNPs = loadBISmartCNPDefinitions(dctOptions.biSmartCnpDefsFile)
    else: lstBISmartCNPs = []

    stNewCNPs = set([cnp.strCNPId for cnp in lstBISmartCNPs])
    if len(stCNPsSeen & stNewCNPs) > 0:
        raise Exception("Some CNP definitions in " + dctOptions.biSmartCnpDefsFile + " overlap a previously-loaded CNP definition")
    stCNPsSeen |= stNewCNPs

    lstLocusCNPs = lstRangeCNPs + lstSmartCNPs

    lstAccumulators = []
    if len(lstBISmartCNPs) > 0:
        lstAccumulators.append(NameCNVAccumulator(lstBISmartCNPs))
    if len(lstLocusCNPs) > 0:
        lstAccumulators.append(LocusCNVAccumulator(lstLocusCNPs))

    if dctOptions.normalizationProbes is not None:
        lstProbes = loadProbes(dctOptions.normalizationProbes)
        if (len(lstProbes)==0):
            print >> sys.stderr, "Normalization Probe file empty!  Skipping normalization."
            lstMedians=None
        else:
            lstMedians = findMediansOfSelectProbes(lstProbeSummariesFiles, set(lstProbes), strMissingValueLabel)
    else:
        lstMedians = None
        
    fIn = InputFileMergeWithPushBack(lstProbeSummariesFiles)
    # Transfer the header from the input to the output
    sloshHeader(fOut, fIn, bNoLocus=dctOptions.no_locus)

    for i, strLine in enumerate(fIn):
        lstFields = strLine.split()
        if dctOptions.ignoreSNPs and lstFields[SUMMARY_PROBESET_TYPE_FIELD_INDEX] in ["A", "B", "S"]:
            continue
        lstFields[SUMMARY_POSN_FIELD_INDEX] = int(lstFields[SUMMARY_POSN_FIELD_INDEX])
        lstFields[SUMMARY_CHR_FIELD_INDEX] = int(utils.convertChromosomeStr(lstFields[SUMMARY_CHR_FIELD_INDEX]))

        for accumulator in lstAccumulators:
            accumulator.accumulate(lstFields)
        
        if i % 10000 == 0:
            print ".",

    print ""
    lstCNVsAndAccumulatedIntensities = []
    for accumulator in lstAccumulators:
        lstCNVsAndAccumulatedIntensities += accumulator.getCNVsAndAccumlatedIntensities()

    # Sort by CNP name so the order is consistent regardless of genome build
    lstCNVsAndAccumulatedIntensities.sort(cmpCNPAndAccumulatedIntensitiesTupByName)

    funcSummarizationAlgorithm = dctSUMMARIZATION_ALGORITHMS[dctOptions.summarizationAlgorithm]
    for cnp, lstRows in lstCNVsAndAccumulatedIntensities:
        setFoundProbes=set ([lstFields[SUMMARY_PROBE_FIELD_INDEX] for lstFields in lstRows])
        #if (cnp.strCNPId=="HM3_CNP_165"):
        #    print ("unaltered")
        #    for lstFields in lstRows: print (lstFields)
         
        lstRows=[extractIntensitiesFromSummaryFields(lstFields, strMissingValueLabel) for lstFields in lstRows]
        if dctOptions.biSmartCnpDefsFile is not None:
            setExpectedProbes=set(cnp.stProbes)
            setMissingProbes=cnp.stProbes.difference(setFoundProbes)
        else:
            setMissingProbes=set()
            
        if (len(lstRows)==0):
            print >> sys.stderr, cnp.strCNPId + " Can't be summarized because there is no available data: "
        else:    
            if (len(setMissingProbes)>0):
                print >> sys.stderr, cnp.strCNPId+ " Is missing probes: " + " ".join(setMissingProbes)
            
            print >> sys.stdout, cnp.strCNPId
            
            lstCNPSummary = funcSummarizationAlgorithm(lstRows, dctOptions.verbose)
            if lstMedians is None:
                lstMedians = [1.0] * len(lstCNPSummary)
                assert(len(lstMedians) == len(lstCNPSummary))
            
            lstNormalizedCNPSummary = [lstCNPSummary[i]/lstMedians[i] for i in xrange(len(lstCNPSummary))]
            lstCNPOutputFields = cnp.getOutputFields()
            if dctOptions.no_locus:
                del lstCNPOutputFields[1:]
            print >> fOut, "\t".join(lstCNPOutputFields +
                                ["%.4f" % f for f in lstNormalizedCNPSummary])
        

    fIn.close()
    fOut.close()
    print >> sys.stdout, "Finished.\n"
    

if __name__ == "__main__":
    sys.exit(main())
    
