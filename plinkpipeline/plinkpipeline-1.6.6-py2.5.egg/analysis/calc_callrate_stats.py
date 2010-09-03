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
"""usage: %prog [options] call-file confidence-file

Calculates call rate statistics from a set of calls and confidences.
"""
from __future__ import division
import sys
#from math import sqrt,log
#from numpy import mean,median
import optparse
import os.path
import pickle
import cPickle

SAMPLE_CALLRATE_SPEC = 0.96
SNP_CALLRATE_SPEC = 0.85
SAMPLE_CONCRATE_SPEC = 0.99

LIB_LOCATION = "/fg/software/Affymetrix/1chip/data/affylib/"
RS_FILE = "Mapping500K_annot.trimmed.pickle"

def mean(x):
    if len(x) == 0:
        return -1.
    x = [val for val in x if val is not None]
    return sum(x) / float(len(x))

dctFLIP = {
    'A': 'T',
    'T': 'A',
    'G': 'C',
    'C': 'G'
    }

def flip_genotype(geno):
    letter1 = dctFLIP[geno[0]]
    letter2 = dctFLIP[geno[1]]
    if letter1 < letter2:
        return letter1 + letter2
    else:
        return letter2 + letter1

def affycode(all_a,all_b,call):
    if call == all_a + all_a:
        return 0
    if (call == all_a + all_b) or (call == all_b + all_a):
        return 1
    if call == all_b + all_b:
        return 2
    return -1

def readSnpFile(strPath):
    f = open(strPath)
    setSnps = set()
    for line in f:
        line = line.split()
        if line[0] == "probeset_id":
            continue
        setSnps.add(line[0])
    f.close()
    return setSnps

def readSampleList(strPath):
    f = open(strPath)
    lstRet = [strLine.strip() for strLine in f]
    f.close()
    return lstRet

# Returns dictionary of reference calls:
# key: snp name (SNP_A-nnn)
# value: list of calls, each call is an integer (0=AA, 1=AB, 2=BB, -1=nocall)
def loadRefcalls(guideFilePath, rsFilePath, libDirPath, snps,
                 lstSampleIndicesToProcess=None):
    print >> sys.stderr, "Loading rs information file " + rsFilePath + " ..."
    rsTable = load_rs_file(rsFilePath, snps)

    print >> sys.stderr, "Loading guide file " + guideFilePath + " ..."
    guideInfo = load_guide_with_answer_db(guideFilePath, lstSampleIndicesToProcess)

    dctFileMap = {}
    for guideIndex,info in enumerate(guideInfo):
        if info is None:
            continue
        path=info[0]
        if not path in dctFileMap:
            dctFileMap[path] = [[],[]]
        dctFileMap[path][0].append(info[1])
        dctFileMap[path][1].append(guideIndex)

    dctRefCalls = {}
    for path, tup in dctFileMap.iteritems():
        path = os.path.join(libDirPath, path)
        print >> sys.stderr, "Loading refcalls from " + path + " ..."

        columnIndexes = tup[0]
        guideIndexes = tup[1]
        f=open(path)
        for line in f:
            hapmap_info = line.split()
            rs = hapmap_info[0]
            if rs in rsTable:
                rs_info = rsTable[rs]
                snp = rs_info[0]
                rs_strand = rs_info[2]
                rs_alleleA = rs_info[3]
                rs_alleleB = rs_info[4]
                if not snp in dctRefCalls:
                    dctRefCalls[snp] = [-1] *  len(guideInfo)
                refcalls = dctRefCalls[snp]
                hapmap_strand = hapmap_info[2]
                hapmap_calls=hapmap_info[3:]
                bWarnedForThisSNP = False
                for i in xrange(len(columnIndexes)):
                    hapmap_call = hapmap_calls[columnIndexes[i]]
                    call = -1;
                    if hapmap_call != 'NN':
                        if rs_strand != hapmap_strand:
                            hapmap_call = flip_genotype(hapmap_call)
                        call = affycode(rs_alleleA, rs_alleleB, hapmap_call)
                        if call == -1 and not bWarnedForThisSNP:
                            print >> sys.stderr, "Mismatch btw RS info and hapmap info", rs_info, hapmap_info
                            bWarnedForThisSNP = True
                    refcalls[guideIndexes[i]] = call
        f.close()

    return dctRefCalls

class HapMapRefCalls(object):
    def __init__(self, guideFilePath, rsFilePath, libDirPath, snps, lstSampleIndicesToProcess=None):
        self._dctRefCalls = loadRefcalls(guideFilePath, rsFilePath, libDirPath, snps, lstSampleIndicesToProcess)

    def hasSNP(self, strSNP):
        return strSNP in self._dctRefCalls

    def getCallsForSNP(self, strSNP):
        return self._dctRefCalls[strSNP]

lstPopulations = [
    ("CEPH", "ceu_master.txt.filtered.trimmed",
     ['NA06985', 'NA06991', 'NA06993', 'NA06994', 'NA07000', 'NA07019', 'NA07022', 'NA07029', 'NA07034', 'NA07048', 'NA07055', 'NA07056', 'NA07345', 'NA07348', 'NA07357', 'NA10830', 'NA10831', 'NA10835', 'NA10838', 'NA10839', 'NA10846', 'NA10847', 'NA10851', 'NA10854', 'NA10855', 'NA10856', 'NA10857', 'NA10859', 'NA10860', 'NA10861', 'NA10863', 'NA11829', 'NA11830', 'NA11831', 'NA11832', 'NA11839', 'NA11840', 'NA11881', 'NA11882', 'NA11992', 'NA11993', 'NA11994', 'NA11995', 'NA12003', 'NA12004', 'NA12005', 'NA12006', 'NA12043', 'NA12044', 'NA12056', 'NA12057', 'NA12144', 'NA12145', 'NA12146', 'NA12154', 'NA12155', 'NA12156', 'NA12234', 'NA12236', 'NA12239', 'NA12248', 'NA12249', 'NA12264', 'NA12707', 'NA12716', 'NA12717', 'NA12740', 'NA12750', 'NA12751', 'NA12752', 'NA12753', 'NA12760', 'NA12761', 'NA12762', 'NA12763', 'NA12801', 'NA12802', 'NA12812', 'NA12813', 'NA12814', 'NA12815', 'NA12864', 'NA12865', 'NA12872', 'NA12873', 'NA12874', 'NA12875', 'NA12878', 'NA12891', 'NA12892']),
    ("CHB-JPT", "jptchb_master.txt.filtered.trimmed",
     ['NA18524', 'NA18526', 'NA18529', 'NA18532', 'NA18537', 'NA18540', 'NA18542', 'NA18545', 'NA18547', 'NA18550', 'NA18552', 'NA18555', 'NA18558', 'NA18561', 'NA18562', 'NA18563', 'NA18564', 'NA18566', 'NA18570', 'NA18571', 'NA18572', 'NA18573', 'NA18576', 'NA18577', 'NA18579', 'NA18582', 'NA18592', 'NA18593', 'NA18594', 'NA18603', 'NA18605', 'NA18608', 'NA18609', 'NA18611', 'NA18612', 'NA18620', 'NA18621', 'NA18622', 'NA18623', 'NA18624', 'NA18632', 'NA18633', 'NA18635', 'NA18636', 'NA18637', 'NA18940', 'NA18942', 'NA18943', 'NA18944', 'NA18945', 'NA18947', 'NA18948', 'NA18949', 'NA18951', 'NA18952', 'NA18953', 'NA18956', 'NA18959', 'NA18960', 'NA18961', 'NA18964', 'NA18965', 'NA18966', 'NA18967', 'NA18968', 'NA18969', 'NA18970', 'NA18971', 'NA18972', 'NA18973', 'NA18974', 'NA18975', 'NA18976', 'NA18978', 'NA18980', 'NA18981', 'NA18987', 'NA18990', 'NA18991', 'NA18992', 'NA18994', 'NA18995', 'NA18997', 'NA18998', 'NA18999', 'NA19000', 'NA19003', 'NA19005', 'NA19007', 'NA19012']),
    ("YRI", "yri_master.txt.filtered.trimmed",
     ['NA18500', 'NA18501', 'NA18502', 'NA18503', 'NA18504', 'NA18505', 'NA18506', 'NA18507', 'NA18508', 'NA18515', 'NA18516', 'NA18517', 'NA18521', 'NA18522', 'NA18523', 'NA18852', 'NA18853', 'NA18854', 'NA18855', 'NA18856', 'NA18857', 'NA18858', 'NA18859', 'NA18860', 'NA18861', 'NA18862', 'NA18863', 'NA18870', 'NA18871', 'NA18872', 'NA18912', 'NA18913', 'NA18914', 'NA19092', 'NA19093', 'NA19094', 'NA19098', 'NA19099', 'NA19100', 'NA19101', 'NA19102', 'NA19103', 'NA19116', 'NA19119', 'NA19120', 'NA19127', 'NA19128', 'NA19129', 'NA19130', 'NA19131', 'NA19132', 'NA19137', 'NA19138', 'NA19139', 'NA19140', 'NA19141', 'NA19142', 'NA19143', 'NA19144', 'NA19145', 'NA19152', 'NA19153', 'NA19154', 'NA19159', 'NA19160', 'NA19161', 'NA19171', 'NA19172', 'NA19173', 'NA19192', 'NA19193', 'NA19194', 'NA19200', 'NA19201', 'NA19202', 'NA19203', 'NA19204', 'NA19205', 'NA19206', 'NA19207', 'NA19208', 'NA19209', 'NA19210', 'NA19211', 'NA19221', 'NA19222', 'NA19223', 'NA19238', 'NA19239', 'NA19240'])]

def load_guide(strGuidePath, lstSampleIndicesToProcess=None):
    f = open(strGuidePath)
    try:
        return [strNA.strip() for iLineNum, strNA in enumerate(f)
                if lstSampleIndicesToProcess is None or iLineNum + 1 in lstSampleIndicesToProcess]
    finally:
        f.close()
        
def load_guide_with_answer_db(strGuidePath, lstSampleIndicesToProcess=None):
    """Reads the guide file, determines which population the samples come from.
    Returns a list of tuples.
    The first element of each tuple is the answer database file path and the second is the offset into the answer database for this sample.
    If the NA number is not recognized, None is put into the slot.
    if lstSampleIndicesToProcess is not None, it is a list of 1-based indices of samples
    to include.
    """
    lstResult = []
    for na in load_guide(strGuidePath, lstSampleIndicesToProcess):
        for tup in lstPopulations:
            if na in tup[2]:
                lstResult.append((tup[1], tup[2].index(na)))
                break
        else:
            print >> sys.stderr, "Sample not found in any group: " + na
            lstResult.append(None)
    
    return lstResult

# Unlike other routines with the same name, this returns a map keyed by rs number.
def load_rs_file(strRSPath, stSNPs):
    rs_table = unpickle_rs_file(strRSPath)
    if rs_table is not None:
        return rs_table
    
    f = open(strRSPath)
    rs_table = {}

    for line in f:
        line = line.split()
        if stSNPs == None or line[0] in stSNPs:
            rs_table[line[1]] = line

    f.close()
    return rs_table

def pickle_rs_file(strRSPath, strRSPicklePath):
    rs_table = load_rs_file(strRSPath, None)
    fOut = open(strRSPicklePath, "wb")
    cPickle.dump(rs_table, fOut, pickle.HIGHEST_PROTOCOL)
    fOut.close()
    
def unpickle_rs_file(strRSPath):
    fin = open(strRSPath, "rb")
    try:
        return cPickle.load(fin)
    except pickle.UnpicklingError:
        return None


class AffyRefCalls(object):
    """Load HapMap calls from file in Affy calls file format."""
    def __init__(self, strGuidePath, strAffyRefCallsPath, stSNPs=None, lstSampleIndicesToProcess=None, bIgnoreMissingRefSamples=False):
        print >> sys.stderr, "Loading reference calls from", strAffyRefCallsPath
        lstNAs = load_guide(strGuidePath, lstSampleIndicesToProcess)
        assert(lstSampleIndicesToProcess is None or len(lstNAs) == len(lstSampleIndicesToProcess))

        fIn = open(strAffyRefCallsPath)
        lstHeaderFields = fIn.next().split()
        if lstHeaderFields[0] != "probeset_id":
            raise Exception("Unexpected header line in " + strAffyRefCallsPath + " " + "\t".join(lstHeaderFields))
        self._lstCallIndices = []
        for strNA in lstNAs:
            try:
                self._lstCallIndices.append(lstHeaderFields.index(strNA) - 1)
            except ValueError:
                if bIgnoreMissingRefSamples:
                    print >> sys.stderr, strNA, "not found in", strAffyRefCallsPath, ", replacing with no-calls"
                    self._lstCallIndices.append(None)
                else:
                    print >> sys.stderr, strNA, "not found in", strAffyRefCallsPath
                    raise
        self._dctLines = {}
        for strLine in fIn:
            (strSNP, strCalls) = strLine.split(None, 1)
            if stSNPs is not None and strSNP not in stSNPs:
                continue
            self._dctLines[strSNP] = strCalls

        print >> sys.stderr, "Done loading reference calls from", strAffyRefCallsPath

    def hasSNP(self, strSNP):
        return strSNP in self._dctLines

    def getCallsForSNP(self, strSNP):
        strCalls = self._dctLines[strSNP]
        lstFields = strCalls.split()
        lst = []
        for i in self._lstCallIndices:
            if i is not None:
                lst.append(int(lstFields[i]))
            else: lst.append(-1)
        return lst
        
def getClusterSizes(lstCalls):
    lstClusterSizes = [0] * 3
    for call in lstCalls:
        # call could be None if there is a mismatch btw hapmap data and RS data, eg for {'SNP_A-2313275', 'rs3960362'}
        if call == -1 or call is None:
            continue
        try:
            lstClusterSizes[call] += 1
        except TypeError:
            print >> sys.stderr, "Error! call", call
            raise
    return lstClusterSizes

class StatsByClusterSize(object):
    def __init__(self):
        self.calls = 0
        self.concordant = 0
        self.concordantWithinThreshold = 0
        self.referenceCalls = 0

def notZero(val):
    if not val:
        return 1
    return val

class CallRateStatsCalculator(object): 
    def __init__(self, callFilePath, confFilePath,
                 threshold=None,
                 snpList=None,
                 refCalls=None,
                 bPerClusterStats=False,
                 lstSampleIndicesToProcess=None):
        '''lstSampleIndicesToProcess is a list of 1-based integer column indices.'''
        self.refCalls = refCalls
        self.bPerClusterStats = bPerClusterStats
        self.processedSamples = None
        self.processedSnps = None
        self.snpCallCounts = None
        self.sampleCallCounts = None

        self.sampleConcCounts = None
        self.sampleConcMatches = None
        self.snpConcCounts = None
        self.snpConcMatches = None
        self.sampleHetCounts = None
        self.sampleHetMatches = None
        self.snpHetCounts = None
        self.snpHetMatches = None


        self.polymorphicSnps = 0
        self.monomorphicSnps = 0

        self.calcConcordance = refCalls != None

        if bPerClusterStats:
            assert self.calcConcordance

        callFile = open(callFilePath)
        confFile = open(confFilePath)

        if lstSampleIndicesToProcess is not None:
            callFile = FilteringCallsFile(callFile, lstSampleIndicesToProcess)
            confFile = FilteringCallsFile(confFile, lstSampleIndicesToProcess)

        # process comment lines and header line
        while True:

            callline = callFile.readline()
            while callline != '' and callline[0] == '#':
                callline = callFile.readline()
            confline = confFile.readline()
            while confline != '' and confline[0] == '#':
                confline = confFile.readline()

            if callline == '' and confline == '':
                break
            if callline == '' or confline == '':
                raise Exception("Call file and confidence file are mismatched")

            calls = callline.split()
            confs = confline.split()
            if len(calls) != len(confs):
                raise Exception("Call file and confidence file are mismatched")
            if len(calls) == 0:
                raise Exception("Invalid call/confidence file")
            if calls[0] != confs[0]:
                raise Exception("Call file and confidence file are mismatched (different snps)")
            # First line
            self.processedSnps = []
            self.processedSamples = confs[1:]
            self.snpCallCounts = []
            self.snpHetCallCounts = []
            self.sampleCallCounts = [0 for x in self.processedSamples]
            self.sampleHetCallCounts = [0 for x in self.processedSamples]
            if self.calcConcordance:
                self.sampleConcCounts = [0 for x in self.processedSamples]
                self.sampleConcMatches = [0 for x in self.processedSamples]
                self.snpConcCounts = []
                self.snpConcMatches = []
                self.sampleHetCounts = [0 for x in self.processedSamples]
                self.sampleHetMatches = [0 for x in self.processedSamples]
                self.snpHetCounts = []
                self.snpHetMatches = []
                self.totalRefCalls = 0
                self.totalRefHetCalls = 0
                if self.bPerClusterStats:
                    # [None] at the beginning is because there are no stats for cluster size = 0
                    self.lstHomStatsByClusterSize = [None] + [StatsByClusterSize() for i in xrange(len(self.processedSamples))]
                    self.lstHetStatsByClusterSize = [None] + [StatsByClusterSize() for i in xrange(len(self.processedSamples))]

            break
            
        iLineCount = 0
        while True:

            callline = callFile.readline()
            while callline != '' and callline[0] == '#':
                callline = callFile.readline()
            confline = confFile.readline()
            while confline != '' and confline[0] == '#':
                confline = confFile.readline()

            if callline == '' and confline == '':
                break
            if callline == '' or confline == '':
                raise Exception("Call file and confidence file are mismatched")

            iLineCount += 1
            if iLineCount % 5000 == 0:
                print >> sys.stderr, "Processing line", iLineCount, "of calls file."
            calls = callline.split()
            confs = confline.split()
            if len(calls) != len(confs):
                raise Exception("Call file and confidence file are mismatched")
            if len(calls) == 0:
                raise Exception("Invalid call/confidence file")
            if calls[0] != confs[0]:
                raise Exception("Call file and confidence file are mismatched (different snps)")
            snp = calls[0]
            if snpList != None and snp not in snpList:
                continue

            self.processedSnps.append(snp)
            snpCallCount = 0
            snpHetCallCount = 0
            snpConcCount = 0
            snpConcMatch = 0
            snpHetCount = 0;
            snpHetMatch = 0;
            snpCallSet = set([])

            for i in xrange(len(calls)):
                if calls[i] == 'NA':
                    calls[i] = '-1'

            for i in xrange(len(confs)):
                if confs[i] == 'NA':
                    confs[i] = '1'

            if self.calcConcordance:
                if refCalls.hasSNP(snp):
                    lstRefCallsForThisSNP = refCalls.getCallsForSNP(snp)
                else:
                    lstRefCallsForThisSNP = None

            if self.bPerClusterStats and lstRefCallsForThisSNP is not None:
                lstReferenceClusterSizes = getClusterSizes(lstRefCallsForThisSNP)

                if lstReferenceClusterSizes[0] != 0:
                    self.lstHomStatsByClusterSize[lstReferenceClusterSizes[0]].referenceCalls += lstReferenceClusterSizes[0]
                if lstReferenceClusterSizes[2] != 0:
                    self.lstHomStatsByClusterSize[lstReferenceClusterSizes[2]].referenceCalls += lstReferenceClusterSizes[2]
                if lstReferenceClusterSizes[1] != 0:
                    self.lstHetStatsByClusterSize[lstReferenceClusterSizes[1]].referenceCalls += lstReferenceClusterSizes[1]
            
            for i in range(1,len(confs)):
                call = int(calls[i])
                if threshold != None:
                    if float(confs[i]) > threshold:
                        call = -1;
                if self.calcConcordance:
                    refcall = -1
                    if lstRefCallsForThisSNP is not None:
                        refcall = lstRefCallsForThisSNP[i-1]
                        if refcall != -1:
                            self.totalRefCalls += 1
                        if refcall == 1:
                            self.totalRefHetCalls += 1
                if call != -1:
                    snpCallSet.add(call)
                    snpCallCount += 1
                    self.sampleCallCounts[i-1] += 1
                    if call == 1:
                        self.sampleHetCallCounts[i-1] += 1
                        snpHetCallCount += 1
                    if self.calcConcordance:
                        if refcall != -1:
                            snpConcCount +=  1
                            self.sampleConcCounts[i-1] += 1
                            if refcall == 1:
                                snpHetCount +=  1
                                self.sampleHetCounts[i-1] += 1
                                if call == refcall:
                                    snpHetMatch += 1
                                    self.sampleHetMatches[i-1] += 1
                            if call == refcall:
                                snpConcMatch += 1
                                self.sampleConcMatches[i-1] += 1

                if self.bPerClusterStats and refcall != -1:
                    assert lstReferenceClusterSizes[refcall] > 0
                    if refcall in (0, 2):
                        statsByClusterSize = self.lstHomStatsByClusterSize[lstReferenceClusterSizes[refcall]]
                    else:
                        assert refcall == 1
                        statsByClusterSize = self.lstHetStatsByClusterSize[lstReferenceClusterSizes[refcall]]
                    bWithinThreshold = threshold is None or (float(confs[i]) < threshold)
                    if int(calls[i]) != -1 and bWithinThreshold:
                        statsByClusterSize.calls += 1
                    if int(calls[i]) == refcall:
                        statsByClusterSize.concordant += 1
                    if int(calls[i]) == refcall and bWithinThreshold:
                        statsByClusterSize.concordantWithinThreshold += 1

            self.snpCallCounts.append(snpCallCount)
            self.snpHetCallCounts.append(snpHetCallCount)
            if len(snpCallSet) == 1:
                self.monomorphicSnps += 1
            if len(snpCallSet) > 1:
                self.polymorphicSnps += 1
            if self.calcConcordance:
                self.snpConcCounts.append(snpConcCount)
                self.snpConcMatches.append(snpConcMatch)
                self.snpHetCounts.append(snpHetCount)

        callFile.close()
        confFile.close()

        # return self.processedSnps, self.processedSamples, self.snpCallCounts, self.sampleCallCounts

        self.sampleCallRates = ratios(self.sampleCallCounts,
                                 [len(self.processedSnps) for x in self.processedSamples])
        self.avgSampleCallRate = mean(self.sampleCallRates)
        self.samplesAboveCRSpec = pctAboveThreshold(self.sampleCallRates, SAMPLE_CALLRATE_SPEC)

        self.snpCallRates = ratios(self.snpCallCounts,
                              [len(self.processedSamples) for x in self.processedSnps])
        avgSnpCallRate = mean(self.snpCallRates)
        self.snpsAboveCRSpec = pctAboveThreshold(self.snpCallRates, SNP_CALLRATE_SPEC)

        if len(self.processedSnps) > 0:
            self.polymorphicSnps = self.polymorphicSnps / float(len(self.processedSnps))
            self.monomorphicSnps = self.monomorphicSnps / float(len(self.processedSnps))

        self.sampleHetCRs = ratios(self.sampleHetCallCounts, self.sampleCallCounts)
        if sum(self.sampleCallCounts) > 0:
            self.hetCallRate = float(sum(self.sampleHetCallCounts)) / sum(self.sampleCallCounts)
        else:
            self.hetCallRate = 0

        if self.calcConcordance:
            self.sampleConcRates = ratios(self.sampleConcMatches, self.sampleConcCounts, fDivideByZeroValue=None)
            self.avgSampleConcRate = mean(self.sampleConcRates)
            self.samplesAboveConcSpec = pctAboveThreshold(self.sampleConcRates, SAMPLE_CONCRATE_SPEC)

            self.snpConcRates = ratios(self.snpConcMatches, self.snpConcCounts, fDivideByZeroValue=None)
            avgSnpConcRate = mean(self.snpConcRates)

            numCorrectHetCalls = sum(self.sampleHetMatches)
            numCorrectCalls = sum(self.sampleConcMatches)
            self.hetCRC = float(numCorrectHetCalls) / notZero(self.totalRefHetCalls)
            self.homCRC = float(numCorrectCalls - numCorrectHetCalls) / notZero(self.totalRefCalls - self.totalRefHetCalls)


    def printResults(self, fout):
        print >>fout, "Number of samples: %d" % len(self.processedSamples)
        print >>fout, "Number of snps: %d" % len(self.processedSnps)
        print >>fout, "Pct polymorphic snps: %0.2f" % (self.polymorphicSnps * 100.0)
        print >>fout, "Pct monomorphic snps: %0.2f" % (self.monomorphicSnps * 100.0)
        print >>fout, "Average call rate: %0.2f" % (self.avgSampleCallRate * 100.0)
        # print >>fout, "Average snp call rate: %0.2f" % (avgSnpCallRate * 100.0)
        print >>fout, "Pct samples with CR > 96%%: %0.2f" % (self.samplesAboveCRSpec * 100.0)
        print >>fout, "Pct snps with CR > 85%%: %0.2f" % (self.snpsAboveCRSpec * 100.0)
        print >>fout, "Het percentage: %0.2f" % (self.hetCallRate * 100.0)

        if self.calcConcordance:
            print >>fout, "Average concordance: %0.2f" % (self.avgSampleConcRate * 100.0)
            print >>fout, "Pct samples with Conc > 99%%: %0.2f" % (self.samplesAboveConcSpec * 100.0)
            print >> fout, "HetCRC -- Pct het calls made correctly and within threshold: %0.2f" % (self.hetCRC * 100)
            print >> fout, "HomCRC -- Pct hom calls made correctly and within threshold: %0.2f" % (self.homCRC * 100)

    def printPerSNPOutput(self, fPerSNP):
        if not self.calcConcordance:
            self.snpConcRates = [0.0] * len(self.snpCallRates)
            self.snpConcCounts = [0] * len(self.snpCallRates)
        print >> fPerSNP, "\t".join(["SNP", "CallRate", "Concordance", "HetPercentage", "NumSamplesWithCallAndHapmapCall"])
        for iSNPNum, strSNP in enumerate(self.processedSnps):
            print >> fPerSNP, "\t".join([strSNP,
                                         str(self.snpCallRates[iSNPNum]),
                                         str(self.snpConcRates[iSNPNum]),
                                         str(float(self.snpHetCallCounts[iSNPNum])/notZero(self.snpCallCounts[iSNPNum])),
                                         str(self.snpConcCounts[iSNPNum])])

    def printPerSampleOutput(self, fPerSample):
        if not self.calcConcordance:
            self.sampleConcRates = [0.0] * len(self.processedSamples)
        print >> fPerSample, "%s\t%s\t%s\t%s" % ("Sample", "CallRate", "Concordance", "HetPercentage", )
        for iSampleNum, strSample in enumerate(self.processedSamples):
            if self.sampleConcRates[iSampleNum] is None:
                strSampleConcRate = "None"
            else:
                strSampleConcRate = "%f" % self.sampleConcRates[iSampleNum]
            print >> fPerSample, "%s\t%f\t%s\t%f" % (strSample, self.sampleCallRates[iSampleNum], strSampleConcRate, self.sampleHetCRs[iSampleNum])

    def printHapmapCalls(self, fHapmapCalls):
        fHapmapCalls.write("probeset_id")
        for strSample in self.processedSamples:
            fHapmapCalls.write("\t" + strSample)
        fHapmapCalls.write("\n")
        for strSNP in self.processedSnps:
            if self.refCalls.hasSNP(strSNP):
                print >> fHapmapCalls, strSNP + "\t" + "\t".join([str(call) for call in self.refCalls.getCallsForSNP(strSNP)])
            else:
                print >> fHapmapCalls, strSNP + "\t" + "\t".join(["-1"] * len(self.processedSamples))

    def printStatsByClusterSize(self, fStatsByClusterSize):
        assert self.bPerClusterStats
        print >> fStatsByClusterSize, "\t".join(["ClusterSize", "HomCallRate", "HomConcordance", "HomConcordanceWithinThreshold", "HomClusters",
                                                 "HetCallRate", "HetConcordance", "HetConcordanceWithinThreshold", "HetClusters"])
        for i in xrange(1, len(self.lstHomStatsByClusterSize)):
            homStats = self.lstHomStatsByClusterSize[i]
            hetStats = self.lstHetStatsByClusterSize[i]
            print >> fStatsByClusterSize, "\t".join([str(val) for val in [
                i, homStats.calls/notZero(homStats.referenceCalls), homStats.concordant/notZero(homStats.referenceCalls), homStats.concordantWithinThreshold/notZero(homStats.referenceCalls), homStats.referenceCalls/i,
                hetStats.calls/notZero(hetStats.referenceCalls), hetStats.concordant/notZero(hetStats.referenceCalls), hetStats.concordantWithinThreshold/notZero(hetStats.referenceCalls), hetStats.referenceCalls/i]])
    
                                                    

def pctAboveThreshold(vec, threshold):
    vec = [val for val in vec if val is not None]
    return len(filter(lambda x : x > threshold, vec)) / float(len(vec))

def ratios(vec1, vec2, fDivideByZeroValue=0.0):
    result = []
    for i in range(len(vec1)):
        if vec2[i] == 0:
            result.append(fDivideByZeroValue)
        else:
            result.append(vec1[i]/float(vec2[i]))
    return result

def subtract(vec1, vec2):
    return [vec1[i] - vec2[i] for i in range(len(vec1))]

class FilteringCallsFile(object):
    def __init__(self, fRaw, lstSampleIndices=None, stSNPs=None):
        self.fRaw = fRaw
        self.lstSampleIndices = lstSampleIndices
        self.stSNPs = stSNPs

    def close(self):
        self.fRaw.close()

    def readline(self):
        while True:
            strLine = self.fRaw.readline()
            if len(strLine) == 0:
                return strLine
            if strLine.startswith('#'):
                return strLine
            if strLine.startswith("probeset_id") or self.stSNPs is None:
                return self.filterLineForSamples(strLine)
            strSNP = strLine.split(maxsplit=1)[0]
            if strSNP in self.stSNPs:
                return self.filterLineForSamples(strLine)

    def filterLineForSamples(self, strLine):
        lstFields = strLine.split()
        lstRet = [lstFields[0]] + [lstFields[i] for i in self.lstSampleIndices]
        return "\t".join(lstRet)

def getSampleIndicesToProcess(lstSamplesToProcess, callFile):
    """Given a list of sample names, find the header line in the calls file,
    and return the 1-based indices of the samples in the list.  The indices
    are returned in ascending order, regardless of the order they appear in
    lstSamplesToProcess.  It is an error if a sample in the list is not found
    in the file."""
    fin = open(callFile)
    for strLine in fin:
        if strLine.startswith("#"):
            continue
        assert(strLine.startswith("probeset_id") or strLine.startswith("cnp_id"))
        break
    else:
        raise Exception("Strange calls file, can't find probeset_id: " + callFile)
    fin.close()
    lstFields = strLine.split()
    lstRet = [lstFields.index(strSample) for strSample in lstSamplesToProcess]
    lstRet.sort()
    return lstRet

def removeDuplicateSamples(lstSampleIndicesToProcess, strGuideFilePath):
    """If there are any duplicates in guideFilePath, and they are both called out in lstSampleIndicesToProcess
    (or lstSampleIndicesToProcess is None), then remove the earlier one.  Returns a new lstSampleIndicesToProcess,
    unless all samples are to be included, in which case it returns None.
    Note that lstSampleIndicesToProcess is 1-based."""
    lstNAs = load_guide(strGuideFilePath)
    
    if lstSampleIndicesToProcess is None:
        # if no lstSampleIndicesToProcess, include all samples to start
        lstSampleIndicesToProcess = range(1, len(lstNAs) + 1)

    # Make a list of the indices for each sample, in reverse order (later sample earlier in list)
    dctIndicesBySample = {}
    for i, strNA in enumerate(lstNAs):
        if i+1 in lstSampleIndicesToProcess:
            dctIndicesBySample[strNA] = [i+1] + dctIndicesBySample.get(strNA, [])

    for lstIndices in dctIndicesBySample.itervalues():
        for iIndex in lstIndices[1:]:
            # Remove all except the first item in the list
            lstSampleIndicesToProcess.remove(iIndex)

    if len(lstSampleIndicesToProcess) == len(lstNAs):
        # Nothing removed
        return None
    return lstSampleIndicesToProcess

def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("-c", "--calc-concordance",
                      action="store_true", dest="calcConcordance", default=False,
                      help="""If true, then calculate concordance statistics.
A guide file must be supplied.  Generally useful for HapMap plates only.""")

    parser.add_option("-r", "--ref-calls",
                      dest="refCallsPath",
                      help="""Calculate concordance using the refererence calls from the given file.""")

    parser.add_option("-g", "--guide-file", dest="guideFilePath",
                      help="""File containing the NA number (one per line) for each cel file on the command line.
The number of lines in the guide file must equal the number of cel files on the command line,
and the order of files on the command line must agree with the order of NA numbers in the guide file.""")

    strFilesRequiredInLibDir = ", ".join([RS_FILE] + [tup[1] for tup in lstPopulations])
    parser.add_option("-l", "--lib-dir", dest="libDir",
                      help="""Directory containing the files with genotype calls for each population,
and the file that maps SNP names to rs numbers.  This directory must contain the following files: """ +
                      strFilesRequiredInLibDir + """.  Default: """ + LIB_LOCATION,
                      default=LIB_LOCATION)

    parser.add_option("-s", "--snp-file", dest="snpFilePath",
                      help="""File containing subset of SNPS to be used in evaluation.
File should contain one snp name per line in the first column.
The file can optionally contain a header with 'probeset_id' in the first line.
Default is to use all snps in the call and confidence files.""",
                      default=None)

    parser.add_option("--sample-file", dest="sampleFilePath",
                      help="""File containing subset of samples to be used in evaluation.
File should contain one sample per line.
Default is to use all samples in the call and confidence files.""",
                      default=None)

    parser.add_option("-t", "--threshold", dest="threshold",
                      help="""Confidence threshold for making a call.
If not supplied, then the values in the call file are used (-1 is a no call).""",
                      default=None)

    parser.add_option("-p", "--per-snp-output", dest="perSNPOutputPath",
                      help="""Write per-SNP call rate and concordance to this file.""",
                      default=None)

    parser.add_option("--per-sample-output", dest="perSampleOutputPath",
                      help="""Write per-sample call rate and concordance to this file.""",
                      default=None)

    parser.add_option("--hapmap-output", dest="hapMapCallsOutputPath",
                      help="""Write Hapmap calls in birdseed call format to this file.""",
                      default=None)

    parser.add_option("--per-cluster-size-output", dest="perClusterSizeOutputPath",
                      help="""Write per-cluster-size call rate and concordance to this file.""",
                      default=None)

    parser.add_option("--summary-output", dest="summaryOutputPath",
                      help="Where to write summary output.  Default: stdout")
    
    parser.add_option("--skip-duplicates", dest="skipDuplicates", action="store_true",
                      help="""If an individual appears more than once in the input calls and confidences file,
                      ignore all but the last appearance of that individual.  guide file is required to determine
                      individual ID.  Default: False""")
    parser.add_option("--ignore_missing_refcalls", action="store_true", default=False,
                      help="""When doing concordance, if there are no reference calls at all for a sample,
emit a warning and continue instead of aborting.  Default: %default""")
    
    options, lstArgs = parser.parse_args(argv)

    argCount = len(lstArgs)-1
    if argCount != 2:
        parser.print_help()
        return 1

    callFile = lstArgs[1]
    confFile = lstArgs[2]

    snps = None
    if not options.snpFilePath is None:
        snps = readSnpFile(options.snpFilePath)

    if options.sampleFilePath is not None:
        lstSamplesToProcess = readSampleList(options.sampleFilePath)
        lstSampleIndicesToProcess = getSampleIndicesToProcess(lstSamplesToProcess, callFile)
    else:
        lstSampleIndicesToProcess = None


    if options.refCallsPath is not None:
        options.calcConcordance = True

    if options.skipDuplicates:
        if not options.guideFilePath:
            print >> sys.stderr, "Error: --guide-file is required with --skip-duplicates."
            parser.print_usage()
            return 1
        lstSampleIndicesToProcess = removeDuplicateSamples(lstSampleIndicesToProcess, options.guideFilePath)
    
    refCalls = None
    if options.calcConcordance:
        if not options.guideFilePath:
            print >> sys.stderr, "Error: Guide file path not specified."
            parser.print_usage()
            return 1
        if options.refCallsPath is None:
            refCalls = HapMapRefCalls(options.guideFilePath,
                                      os.path.join(options.libDir, RS_FILE),
                                      options.libDir,
                                      snps,
                                      lstSampleIndicesToProcess=lstSampleIndicesToProcess)
        else:
            refCalls = AffyRefCalls(options.guideFilePath, options.refCallsPath, snps,
                                    lstSampleIndicesToProcess=lstSampleIndicesToProcess,
                                    bIgnoreMissingRefSamples=options.ignore_missing_refcalls)

    if options.perClusterSizeOutputPath and not options.calcConcordance:
        print >> sys.stderr, "if using --per-cluster-size-output, --calc-concordance is required."
        return 1
        
    
    threshold = options.threshold
    if not threshold is None:
        threshold = float(threshold)
    calculator = CallRateStatsCalculator(callFile, confFile, threshold,
                                         snpList=snps,
                                         refCalls=refCalls,
                                         bPerClusterStats=options.perClusterSizeOutputPath is not None,
                                         lstSampleIndicesToProcess=lstSampleIndicesToProcess)

    if options.summaryOutputPath is None:
        fout = sys.stdout
    else:
        fout = open(options.summaryOutputPath, "w")
    calculator.printResults(fout)
    if options.summaryOutputPath is not None:
        fout.close()
        
    if options.perSNPOutputPath is not None:
        fout = open(options.perSNPOutputPath, "w")
        calculator.printPerSNPOutput(fout)
        fout.close()

    if options.perSampleOutputPath is not None:
        fout = open(options.perSampleOutputPath, "w")
        calculator.printPerSampleOutput(fout)
        fout.close()

    if options.hapMapCallsOutputPath is not None:
        fout = open(options.hapMapCallsOutputPath, "w")
        calculator.printHapmapCalls(fout)
        fout.close()

    if options.perClusterSizeOutputPath is not None:
        fout = open(options.perClusterSizeOutputPath, "w")
        calculator.printStatsByClusterSize(fout)
        fout.close()
        
if __name__ == '__main__':
    sys.exit(main())
    
        
