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
"""%prog [options]

Create a list of SNP/sample pairs that should be excluded from birdseed clustering and calling
because they have unusual copy number.
"""

from __future__ import division
import fileinput
import optparse
import sys

from birdsuite import cnv_definition_collection
from mpgutils import utils

lstRequiredOptions = ["cnvDefinitionsFile", "cnvCallsFile", "cnvConfsFile", "genderFile", "specialSNPsFile",
                      "specialCNProbesFile", "probe_locus"]

fDEFAULT_CONFIDENCE_THRESHOLD = 0.1

def loadCNARYOutputFile(strPath, strFileType):
    dctRet = {}
    fIn = fileinput.FileInput([strPath])
    strHeader = utils.skipLeadingComments(fIn)
        
    lstHeaders = strHeader.split()
    if lstHeaders[0] != 'cnp_id':
        utils.raiseExceptionWithFileInput(fIn, strFileType, "Unexpected header line")
                        
    iNumFields = len(lstHeaders)
    for strLine in fIn:
        lstFields = strLine.split()
        if len(lstFields) != len(lstHeaders):
            utils.raiseExceptionWithFileInput(fIn, strFileType, "Number of columns does not match header line")
        if lstFields[0] in dctRet:
            utils.raiseExceptionWithFileInput(fIn, strFileType, "CNV appears more than once")
        if lstFields[1] != "NA":
            dctRet[lstFields[0]] = lstFields[1:]

    fIn.close()
    return dctRet

def stringToIntNATolerant(x):
    if x=="NA": return (x)
    return (int(x))

def stringToFloatNATolerant(x):
    if x=="NA": return(x)
    return (float(x))

def loadCNVCalls(strPath):
    """Returns a dictionary where key is CNV name and value is array of
    ints representing copy number for each sample."""
    dctRaw = loadCNARYOutputFile(strPath, "CNV calls file")
    dctRet = {}
    for strKey, lstValues in dctRaw.iteritems():
        
        dctRet[strKey] = [stringToIntNATolerant(strValue) for strValue in lstValues]
    return dctRet

def loadCNVConfidences(strPath):
    """Returns a dictionary where key is CNV name and value is array of
    floats representing confidence for each sample."""
    dctRaw = loadCNARYOutputFile(strPath, "CNV confidences file")
    dctRet = {}
    for strKey, lstValues in dctRaw.iteritems():
        dctRet[strKey] = [stringToFloatNATolerant(strValue) for strValue in lstValues]
    return dctRet

class ExcludeListCreator(object):
    def __init__(self, cnvDefinitionsFile, cnvCallsFile, cnvConfsFile, genderFile, specialSNPsFile, specialCNProbesFile,
                 fConfidenceThreshold, fProbeCNVMap=None):
        self.cnvDefs = cnv_definition_collection.CNVDefinitionCollection(cnvDefinitionsFile)

        self.dctCNVCalls = loadCNVCalls(cnvCallsFile)
        self.dctCNVConfs = loadCNVConfidences(cnvConfsFile)
        #if there were no canary calls, don't run checks.
        if len(self.dctCNVCalls)!=0:
            
            lstCalls1 = self.dctCNVCalls.values()[0]
            lstConfs1 = self.dctCNVConfs.values()[0]
            if len(lstCalls1) != len(lstConfs1):
                raise Exception("Calls and confs files have different number of columns: " + len(lstCalls1) + "; " +
                                len(lstConfs1))

        # This seems to be allowed in Finny's latest version of Canary 07-11-13
        #if len(self.dctCNVCalls) > len(self.dctCNVConfs):
        #    raise Exception("Calls file has more non-NA rows than confs file: " + str(len(self.dctCNVCalls)) + "; " +
        #                    str(len(self.dctCNVConfs)))

        self.lstGenders = utils.loadGenders(genderFile)
        if len(self.dctCNVCalls)>0 and len(lstCalls1) != len(self.lstGenders):
            raise Exception("Calls file and gender file have different number of samples: " + str(len(lstCalls1)) + "; " +
                        str(len(self.lstGenders)))

        self.dctSpecialProbes = {}
        utils.loadSpecialProbes(self.dctSpecialProbes, specialSNPsFile)
        utils.loadSpecialProbes(self.dctSpecialProbes, specialCNProbesFile)

        self.fConfidenceThreshold = fConfidenceThreshold
        self.fProbeCNVMap = fProbeCNVMap

        # Don't emit a probe more than once, even if it appears in probe definition file multiple times
        self._stProbesSeen = set()

    def processProbeDefinitionFile(self, fOut, strProbeDefinitionFile):
        for lstFields in utils.iterateProbeLocus(strProbeDefinitionFile):
            strProbeName = lstFields[0]
            if strProbeName in self._stProbesSeen:
                print >> sys.stderr, "WARNING:", strProbeName, \
                      "appears more than once in probe definition file(s).  Subsequent definitions ignored."
                continue
            self._stProbesSeen.add(strProbeName)
            strChr = lstFields[1]
            if strChr == '0':
                # Skip probe with no position
                continue
            iPosn = lstFields[2]
            stExcludeSampleIndices = self._getExcludedSamplesForProbe(strProbeName, strChr, iPosn)
            if stExcludeSampleIndices is not None and len(stExcludeSampleIndices) > 0:
                lstExcludSampleIndices = [iIndex for iIndex in stExcludeSampleIndices]
                lstExcludSampleIndices.sort()
                print >>fOut, strProbeName + "\t" + ",".join([str(iIndex) for iIndex in lstExcludSampleIndices])

    def _getExcludedSamplesForProbe(self, strProbeName, strChr, iPosn):
        stRet = set()
        stCNVs = self.cnvDefs.getCNVsForLocus(strChr, iPosn)
        if len(stCNVs) == 0:
            return None
        if self.fProbeCNVMap is not None:
            print >>self.fProbeCNVMap,  strProbeName + "\t" + ",".join([cnv.strCNVName for cnv in stCNVs])
        # If not in special probes file, assume expected count is 2,2 
        tupExpectedCN = self.dctSpecialProbes.get(strProbeName, (2,2))

        for cnv in stCNVs:
            strCNV = cnv.strCNVName
            if strCNV not in self.dctCNVCalls or strCNV not in self.dctCNVConfs:
                # unable to cluster this CNV
                continue
            
            lstCalls = self.dctCNVCalls[strCNV]
            lstConfs = self.dctCNVConfs[strCNV]

            for i in xrange(len(lstCalls)):
                # if CN for this sample does not equal expected CN for this probe and gender,
                # then add to exclude list
                if lstCalls[i] != tupExpectedCN[self.lstGenders[i]] or \
                       lstConfs[i] > self.fConfidenceThreshold:
                    stRet.add(i)
        return stRet
            
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--cnv-defs", dest="cnvDefinitionsFile",
                      help="""(Required) Whitespace-delimited file containing the genomic range of CNVs that are called.
Columns are CNV name, chromosome, start position (inclusive), end position  (inclusive).  Order of lines is arbitrary.""")
    parser.add_option("--probe_locus", 
                      help="""(Required) Whitespace-delimited file containing the locus of SNPs to be birdseeded.
The first 2 columns are SNP name, chromosome, position.  Order of lines is arbitrary.  It is acceptable for this file
to contain CN probes in addition to SNP probes.""")
    parser.add_option("--cnv-calls", dest="cnvCallsFile",
                      help="""(Required) Copy number calls for the samples to be birdseeded.
The samples in this file must be in the same order as in the allele summary file.""")
    parser.add_option("--cnv-confs", dest="cnvConfsFile",
                      help="""(Required) Copy number confidences for the samples to be birdseeded.
The samples in this file must be in the same order as in the allele summary file.""")
    parser.add_option("--gender-file", dest="genderFile",
                      help="""(Required) File containing a line for each sample in the calls file.
0=female, 1=male, 2=unknown.  This file must have a header line "gender".
Order must agree with order of cnv-calls file.""")
    parser.add_option("--special-snps", dest="specialSNPsFile",
                      help="""(Required)  File containing snps with unusual copy number (X, Y, mito).""")
    parser.add_option("--special-cn-probes", dest="specialCNProbesFile",
                      help="""(Required)  File containing cn probes with unusual copy number (X, Y, mito).""")
    parser.add_option("--conf-threshold", dest="confidenceThreshold", type="float", default=fDEFAULT_CONFIDENCE_THRESHOLD,
                      help="""Exclude any sample that has confidence threshold > this.  Default: """ +
                      str(fDEFAULT_CONFIDENCE_THRESHOLD))
    parser.add_option("-o", dest="outputFile",
                      help="""Where to write output.  Default: stdout""")
    parser.add_option("--probe-cnv-map", dest="probeCNVMapFile",
                      help="""If present, write a map of SNP and CN proves to CNVs.""")

    dctOptions, lstArgs = parser.parse_args(argv)

    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if len(lstArgs) > 1:
        print >> sys.stderr, "ERROR: Unexpected argument on command line."
        parser.print_help()
        return 1

    if dctOptions.probeCNVMapFile:
        fProbeCNVMap = open(dctOptions.probeCNVMapFile, "w")
    else:
        fProbeCNVMap = None

    excludeListCreator = ExcludeListCreator(dctOptions.cnvDefinitionsFile,
                                            dctOptions.cnvCallsFile,
                                            dctOptions.cnvConfsFile,
                                            dctOptions.genderFile,
                                            dctOptions.specialSNPsFile,
                                            dctOptions.specialCNProbesFile,
                                            dctOptions.confidenceThreshold,
                                            fProbeCNVMap=fProbeCNVMap)

    if dctOptions.outputFile:
        fOut = open(dctOptions.outputFile, "w")
    else:
        fOut = sys.stdout

    print >> fOut, "probeset_id\texclude_list"
    
    excludeListCreator.processProbeDefinitionFile(fOut, dctOptions.probe_locus)

    if dctOptions.outputFile:
        fOut.close()

    if dctOptions.probeCNVMapFile:
        fProbeCNVMap.close()
        
if __name__ == "__main__":
    sys.exit(main())
    
