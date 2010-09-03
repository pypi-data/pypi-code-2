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

Count mendel failures in Canary, Larry_bird or Birdseed calls.  If one makes no
assumptions regarding how the copies of a SNP or CNV will be distributed between the two
copies of an autosome, the ability to detect mendel failures is limited.  For Larry_bird
and Birdseed calls, the --assume_triallelic option increases the ability to detect mendel
failures.

Three files are produced, with the following contents:

BASENAME.mendel contains one line for each mendel failure.  The columns are:
    Family ID
    Individual ID
    Probe
    Usual female copy number
    Usual male copy number
    Zero-based individual index
    Individual call
    Mother call
    Father call
    Error code
    Error string

BASENAME.lmendel contains one line for each probe with errors.  The columns are:
    Probe
    Number of errors

BASENAME.imendel contains one line for each child or individual with errors.
Errors are always assigned to the child.  The columns are:
    Family ID
    Individual ID
    Number of errors

If --assume_triallelic is passed, the file BASENAME.hwe is also created.  The columns are:
    Probe
    Count of triallelic genotype classes
    Chi-squared
    P-value
    Frequency of null allele
    Frequency of A allele
    Frequency of B allele
"""

from __future__ import division
import math
import operator
import optparse
import scipy.stats.stats
import sys

import calls_confidences_filter
from mpgutils import utils

lstRequiredOptions=["calls", "confs", "tfam", "special_probes", "output"]

iFAMILY_ID_INDEX=utils.iTFAM_FAMILY_ID_INDEX
iINDIVIDUAL_ID_INDEX=utils.iTFAM_INDIVIDUAL_ID_INDEX
iPATERNAL_ID_INDEX=utils.iTFAM_PATERNAL_ID_INDEX
iMATERNAL_ID_INDEX=utils.iTFAM_MATERNAL_ID_INDEX
iGENDER_INDEX=utils.iTFAM_GENDER_INDEX
# Index of father & mother in list of individuals
iPATERNAL_INDEX_INDEX=iGENDER_INDEX+1
iMATERNAL_INDEX_INDEX=iPATERNAL_INDEX_INDEX+1

iFEMALE = 0
iMALE = 1
iNUM_GENDERS = 2

def otherGender(iGender):
    """Returns female if iGender is male, and vice versa"""
    return 1 - iGender

def convertParentID(strID):
    if strID == "0":
        return None
    return strID


class CanaryCall(object):
    def __init__(self, strCall, iUsualCopies=2):
        self._iCall = int(strCall)

    def isNoCall(self):
        return self._iCall == -1

    def isZeroCopies(self):
        return self._iCall == 0

    def __gt__(self, other):
        return self._iCall > other._iCall

    def __add__(self, other):
        assert(not self.isNoCall() and not other.isNoCall())
        return self.__class__(self._iCall + other._iCall)

    def __str__(self):
        return str(self._iCall)

    def noCall(cls):
        return cls(-1)

    noCall = classmethod(noCall)

class LarryBirdCall(object):
    def __init__(self, theCall, iUsualCopies=2, bBirdseedCall=False):
        if not bBirdseedCall or isinstance(theCall, list) or isinstance(theCall, tuple):
            if isinstance(theCall, str):
                self._lstCalls = [int(call) for call in theCall.split(",")]
            else:
                self._lstCalls = theCall[:]
        else:
            if isinstance(theCall, str):
                theCall = int(theCall)
            if theCall == -1:
                self._lstCalls = [-1,-1]
            elif theCall == 0:
                self._lstCalls = [2,0]
            elif theCall == 1:
                self._lstCalls = [1,1]
            else:
                if theCall != 2:
                    raise Exception("Strange birdseed call: " + str(theCall))
                self._lstCalls = [0,2]

    def isNoCall(self):
        return self._lstCalls == [-1,-1]

    def isZeroCopies(self):
        return self._lstCalls == [0,0]

    def __gt__(self, other):
        """Warning: This method is not symmetric"""
        for i in xrange(len(self._lstCalls)):
            if self._lstCalls[i] > other._lstCalls[i]:
                return True
        return False

    def __add__(self, other):
        assert(not self.isNoCall() and not other.isNoCall())
        lstCombined = [self._lstCalls[i] + other._lstCalls[i] for i in xrange(len(self._lstCalls))]
        return self.__class__(lstCombined)

    def __eq__(self, other):
        return self._lstCalls == other._lstCalls

    def __hash__(self):
        """This must be defined in order for set membership to work properly"""
        return self._lstCalls[0] + 100000 * self._lstCalls[1]
    
    def __str__(self):
        return ",".join([str(val) for val in self._lstCalls])

    def noCall(cls):
        return cls([-1,-1])

    noCall = classmethod(noCall)

    def totalCopies(self):
        assert(not self.isNoCall())
        return self._lstCalls[0] + self._lstCalls[1]

    def triallelicIterate(self, iExpectedCopies):
        """Based on the assumption that this call represents at most a tri-allelic
        situation {A,B,0}, iterate through a list of LarryBirdCall objects that represent
        the possible alleles that might be inherited by the child of a parent with this LarryBird call."""
        assert(iExpectedCopies <= 2)
        assert(iExpectedCopies > 0)
        assert(self.isNoCall() or self.totalCopies() <= iExpectedCopies)

        # Only if this call has less than the expected copies is null considered a possible allele
        if self.isNoCall() or self.totalCopies() < iExpectedCopies:
            yield LarryBirdCall([0,0])

        if self.isNoCall():
            # All alleles are possible from a no-call
            lstCalls = [1,1]
        else:
            lstCalls = self._lstCalls[:]
            
        for i in xrange(len(lstCalls)):
            if lstCalls[i] > 0:
                lstRet = [0,0]
                lstRet[i] = 1
                yield LarryBirdCall(lstRet)

    def hweAlleleCount(self):
        """Return a vector with the number of null, A and B copies.
        Assumed to be a triallelic SNP, either autosomal or chrX female."""
        assert(not self.isNoCall())
        assert(self.totalCopies() <= 2)

        if self.isZeroCopies():
            return [2,0,0]
        if self.totalCopies() == 1:
            return [1] + self._lstCalls
        return [0] + self._lstCalls

    def isHet(self):
        """Assumed to be a triallelic SNP, either autosomal or chrX female.
        Returns False if call is null/null, A/A or B/B, else True"""
        assert(not self.isNoCall())
        assert(self.totalCopies() <= 2)

        if self.isZeroCopies():
            return False
        if self.totalCopies() < 2:
            return True
        for iCount in self._lstCalls:
            if iCount == 2:
                return False
        return True

class BirdseedCall(LarryBirdCall):
    def __init__(self, thisCall, iUsualCopies=2):
        super(BirdseedCall, self).__init__(thisCall, bBirdseedCall=True)
        if iUsualCopies == 0:
            if not self.isNoCall():
                # Not raising exception because this can happen due to gender mix-up
                print >> sys.stderr, "Birdseed call should have no-call for female chrY"
        elif iUsualCopies == 1 and not self.isNoCall():
            if self._lstCalls == [1,1]:
                # Not raising exception because this can happen due to gender mix-up
                print >> sys.stderr, "Birdseed should not have het call for haploid SNP"
            elif self._lstCalls == [2,0]:
                self._lstCalls = [1,0]
            else:
                if self._lstCalls != [0,2]:
                    raise Exception("Birdseed call should never have unusual copy number: " + str(self._lstCalls))
                self._lstCalls = [0,1]
                
        

def triallelicMendelError(thisCall, lstParentCalls, tupUsualCopiesByGender, iThisGender):
    """Return True if there is a Mendel error based on the assumption that SNP is triallelic {0,A,B}"""

    # Shouldn't happen but may as well check
    
    if thisCall.isNoCall():
        return False

    # If both parents are no-calls, can't conclude anything
    for parentCall in lstParentCalls:
        if not parentCall.isNoCall():
            break
    else:
        return False

    # Don't try this test if one of the parents has greater than usual copy number
    for i in xrange(iNUM_GENDERS):
        if not lstParentCalls[i].isNoCall() and lstParentCalls[i].totalCopies() > tupUsualCopiesByGender[i]:
            return False

    # Don't try this test if the child has greater than usual copy number
    if thisCall.totalCopies() > tupUsualCopiesByGender[iThisGender]:
        return False

    stPossibleCalls = set()

    # Make a local copy so it can be changed without messing up caller
    lstParentCalls = lstParentCalls[:]

    if tupUsualCopiesByGender[iFEMALE] == 1 and tupUsualCopiesByGender[iMALE] == 1:
        # chrMT
        # Set of possible calls is just the maternal allele
        if lstParentCalls[iFEMALE].isNoCall():
            return False
        stPossibleCalls.update(set([allele for allele in lstParentCalls[iFEMALE].triallelicIterate(1)]))
    else:
        if tupUsualCopiesByGender[iThisGender] == 2:
            # autosomal or female chrX
            # Set of possible calls is cross product of possible maternal alleles and possible paternal alleles
            for momCall in lstParentCalls[iFEMALE].triallelicIterate(tupUsualCopiesByGender[iFEMALE]):
                for dadCall in lstParentCalls[iMALE].triallelicIterate(tupUsualCopiesByGender[iMALE]):
                    stPossibleCalls.add(momCall + dadCall)
        else:
            assert(iThisGender == iMALE)
            assert(tupUsualCopiesByGender[iMALE] == 1)
            if tupUsualCopiesByGender[iFEMALE] == 2:
                # chrX
                stPossibleCalls.update(set([allele for allele in lstParentCalls[iFEMALE].triallelicIterate(2)]))
            else:
                # chrY
                assert(tupUsualCopiesByGender[iFEMALE] == 0)
                stPossibleCalls.update(set([allele for allele in lstParentCalls[iMALE].triallelicIterate(1)]))


    return thisCall not in stPossibleCalls
        
        


    
def mendelCheck(lstPed, lstCalls, tupUsualCopiesByGender, noCall, bTryTriallelic):
    """Returns a list of the indices of the child in a Mendel error situation.
    Each list element is a tuple containing
    (childIndex, childCall, fatherCall, motherCall, error code, error description)."""
    lstRet = []
    for i, thisCall in enumerate(lstCalls):
        if thisCall.isNoCall():
            continue
        tupPed = lstPed[i]
        iThisGender = tupPed[iGENDER_INDEX]
        if iThisGender is not None:
            if tupUsualCopiesByGender[iThisGender] == 0:
                if not thisCall.isZeroCopies():
                    # Detect non-zero copy number for chrY and female
                    lstRet.append((i, thisCall, None, None, 1, "Non-zero copy number for sample that should have 0"))
                continue

        lstParentCalls = [noCall, noCall]
        if tupPed[iPATERNAL_INDEX_INDEX] is not None:
            tupPaternalPed = lstPed[tupPed[iPATERNAL_INDEX_INDEX]]
            lstParentCalls[iMALE] = lstCalls[tupPed[iPATERNAL_INDEX_INDEX]]
        else: tupPaternalPed = None

        if tupPed[iMATERNAL_INDEX_INDEX] is not None:
            tupMaternalPed = lstPed[tupPed[iMATERNAL_INDEX_INDEX]]
            lstParentCalls[iFEMALE] = lstCalls[tupPed[iMATERNAL_INDEX_INDEX]]
        else: tupMaternalPed = None

        lstParentPeds = [tupMaternalPed, tupPaternalPed]

        if lstParentCalls[iMALE].isNoCall() and lstParentCalls[iFEMALE].isNoCall():
            continue

        bFoundError = False
        for iGender in xrange(iNUM_GENDERS):
            iOtherGender = otherGender(iGender)
            if tupUsualCopiesByGender[iOtherGender] == 0:
                if not lstParentCalls[iGender].isNoCall() and thisCall > lstParentCalls[iGender]:
                    lstRet.append((i, thisCall, lstParentCalls[iFEMALE], lstParentCalls[iMALE], 2, "Child has more copies than parent in single-parent inheritance situation"))
                    bFoundError = True
                    break
        if bFoundError:
            continue

        if iThisGender == iMALE and tupUsualCopiesByGender[iMALE] == 1 and tupUsualCopiesByGender[iFEMALE] == 2 and \
               not lstParentCalls[iFEMALE].isNoCall() and thisCall > lstParentCalls[iFEMALE]:
            lstRet.append((i, thisCall, lstParentCalls[iFEMALE], lstParentCalls[iMALE], 3, "Male child has more copies than mother of chrX probe"))
            continue

        # chrMT
        if tupUsualCopiesByGender[iMALE] == 1 and tupUsualCopiesByGender[iFEMALE] == 1 and \
               not lstParentCalls[iFEMALE].isNoCall() and thisCall > lstParentCalls[iFEMALE]:
            lstRet.append((i, thisCall, lstParentCalls[iFEMALE], lstParentCalls[iMALE], 6, "Child has more copies than mother of MT probe"))
            continue
            

        # default autosomal case.  Need both parents in order to check
        if not lstParentCalls[iMALE].isNoCall() and not lstParentCalls[iFEMALE].isNoCall() \
               and thisCall > lstParentCalls[iMALE] + lstParentCalls[iFEMALE]:
            lstRet.append((i, thisCall, lstParentCalls[iFEMALE], lstParentCalls[iMALE], 4, "Child has more copies than sum of parents for autosomal probe"))
            continue

        if bTryTriallelic and triallelicMendelError(thisCall, lstParentCalls, tupUsualCopiesByGender, iThisGender):
            lstRet.append((i, thisCall, lstParentCalls[iFEMALE], lstParentCalls[iMALE], 5, "Tri-allelic Mendel error"))
            continue


    return lstRet

def isTriallelic(lstPed, lstObjCalls, tupUsualCopiesByGender, noCall):
    for i, call in enumerate(lstObjCalls):
        if call.isNoCall():
            continue
        tupPed = lstPed[i]
        iGender = tupPed[iGENDER_INDEX]
        if iGender == iFEMALE or iGender == iMALE:
            iUsualCalls = tupUsualCopiesByGender[iGender]
        else:
            iUsualCalls = 2

        if call.totalCopies() > iUsualCalls:
            return False
    return True

# The 3 alleles for a tri-allelic SNP
lstThreeAlleles = [LarryBirdCall([0,0]), LarryBirdCall([1,0]), LarryBirdCall([0,1])]
stTriallelicGenotypeClasses = set([call1 + call2 for call1 in lstThreeAlleles for call2 in lstThreeAlleles])
strTriallelicGenotypeClasses = "/".join([str(call) for call in stTriallelicGenotypeClasses])

def hardy_weinberg(lstPed, lstObjCalls, tupUsualCopiesByGender):
    """Returns a list of [counts by class, chi-squared]"""
    if tupUsualCopiesByGender[iFEMALE] != 2 and tupUsualCopiesByGender[iMALE]  != 2:
        # Can't do HWE for chrY and MT
        return None

    dctCountByClass = {}
    for genotypeClass in stTriallelicGenotypeClasses:
        dctCountByClass[genotypeClass] = 0
            
    bFemalesOnly = tupUsualCopiesByGender[iMALE]  != 2
        

    for i, call in enumerate(lstObjCalls):
        if call.isNoCall():
            continue
        if bFemalesOnly and lstPed[i][iGENDER_INDEX] == iMALE:
            continue

        # Skip non-founders
        if not bFemalesOnly and lstPed[i][iPATERNAL_INDEX_INDEX] is not None:
            continue
        if lstPed[i][iMATERNAL_INDEX_INDEX] is not None:
            continue
        dctCountByClass[call] += 1

    iTotalCalls = reduce(operator.add, dctCountByClass.values(), 0)
    if iTotalCalls == 0:
        return None
    
    # null, A, B
    lstAlleleCounts = [0,0,0]
    for call, iNum in dctCountByClass.iteritems():
        lstCountsForCall = call.hweAlleleCount()
        for i in xrange(len(lstAlleleCounts)):
            lstAlleleCounts[i] += iNum * lstCountsForCall[i]

    iTotalAlleles = reduce(operator.add, lstAlleleCounts, 0)
    lstProbabilities = [float(iAlleleCount)/iTotalAlleles for iAlleleCount in lstAlleleCounts]

    fChiSquared = 0.0

    for call, iObserved in dctCountByClass.iteritems():
        fExpected = 1.0
        for i, iAlleleCount in enumerate(call.hweAlleleCount()):
            if iAlleleCount == 0:
                continue
            if lstProbabilities[i] == 0.0:
                assert(iObserved == 0)
            fExpected *= math.pow(lstProbabilities[i], iAlleleCount)
        if call.isHet():
            fExpected *= 2
        assert(fExpected != 0.0 or iObserved == 0)
        if fExpected != 0.0:
            fChiSquared += math.pow(iObserved - fExpected * iTotalCalls, 2) / (iTotalCalls * fExpected)

    fPValue = scipy.stats.stats.chisqprob(fChiSquared, 2)

    return ["/".join([str(iCount) for iCount in dctCountByClass.values()]), fChiSquared, fPValue] + lstProbabilities
    
                        
def convertConfidenceToFloat(strConf):
    if strConf == "NA":
        return 1.0
    return float(strConf)
                
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-c", "--calls",
                      help="""(Required) Input calls file from Canary or Larry_bird.""")
    parser.add_option("--confs",
                      help="""(Required) Input confs file in traditional apt-probeset-genotype format.""")
    parser.add_option("--tfam",
                      help="""(Required) Input pedigree file in tfam format.  Lines of this file should be in
the same order as samples in calls and confs file.""")
    parser.add_option("--special_probes",
                      help="""(Required) special_probes file.  For larry_bird calls, this is special_snps.
For Canary calls, this is special_cn_probes file.""")
    parser.add_option("-o", "--output",
                      help="""(Required) Basename for output files.  Output files will be
BASENAME.mendel, BASENAME.imendel and BASENAME.lmendel.""")
    parser.add_option("--assume_triallelic", default=False, action="store_true",
                      help="""If enabled, if a SNP has no calls with copy number > 2, assume alleles are {0, A, B},
which allows for stricter Mendel check.  This is only valid for larry_bird calls.  Default: %default.""")
    parser.add_option("-b", "--birdseed", default=False, action="store_true",
                      help="""If enabled, assume the calls file is Birdseed calls.  Selecting this option also
enables --assume_triallelic.  Default: %default.""")
    parser.add_option("-t", "--threshold", type="float", default=0.1,
                      help="""A call with confidence value above this threshold is considered a no-call.""")
    parser.add_option("--samples", 
                      help="""File containing subset of samples to be included in the output.
File should contain one sample per line.
Default is to use all samples in the call and confidence files.""")
    parser.add_option("--probes", 
                      help="""File containing subset of probes to be included in the output.
File should contain one probe name per line in the first column.
The file can optionally contain a header with 'probeset_id' or 'cnp_id' in the first line.
Default is to use all probes in the call and confidence files.""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if dctOptions.birdseed:
        dctOptions.assume_triallelic = True
        
    fileObjectFactory = calls_confidences_filter.FilteringCallsAndConfidencesFileFactory(strCallsPath=dctOptions.calls,
                                                                                         strConfidencesPath=dctOptions.confs,
                                                                                         strSamplesListPath=dctOptions.samples,
                                                                                         strSNPsListPath=dctOptions.probes)
    fCalls = fileObjectFactory.fCalls
    fConfs = fileObjectFactory.fConfidences

    # This list is 1-based, so convert to 0-based before filtering tfam
    if fileObjectFactory.lstSampleIndicesToProcess is not None:
        lstSampleIndicesToProcess = [val - 1 for val in fileObjectFactory.lstSampleIndicesToProcess]
    else: lstSampleIndicesToProcess = None
    
    lstPed = utils.load_tfam(dctOptions.tfam, lstIndicesToLoad=lstSampleIndicesToProcess)
    dctSpecialProbes = utils.loadSpecialProbes(None, dctOptions.special_probes)

    fMendel = open(dctOptions.output + ".mendel", "w")
    print >> fMendel, "\t".join(["FID", "KID", "SNP", "ExpectedFemaleCopies", "ExpectedMaleCopies", "KIDIndex",
                                 "KIDCall", "MatCall", "PatCall", "ErrCode", "ErrMsg"])
    fLMendel = open(dctOptions.output + ".lmendel", "w")
    print >> fLMendel, "\t".join(["SNP", "NumErrors"])
    fHWE = None

    strHeader = utils.skipLeadingComments(fCalls)
    iNumSamples = len(strHeader.split()) - 1
    strConfsHeader = utils.skipLeadingComments(fConfs)
    if strHeader != strConfsHeader:
        raise Exception("Mismatch between calls and confs header lines")

    lstErrorsPerSample = [0] * iNumSamples

    lstGenders = []
    for tupPed in lstPed:
        iGender = tupPed[iGENDER_INDEX]
        if iGender is None:
            iGender = iFEMALE
        lstGenders.append(iGender)    

    bIsCanaryCall = None

    for strLine in fCalls:
        lstFields = strLine.split()
        lstCalls = lstFields[1:]

        if bIsCanaryCall is None:
            # Haven't decided yet if input is canary calls or larry_bird calls
            if dctOptions.birdseed:
                bIsCanaryCall = False
            else: bIsCanaryCall = (lstCalls[0].find(",") == -1)
            if bIsCanaryCall:
                strNoCall = "-1"
                if dctOptions.assume_triallelic:
                    raise Exception("--assume_triallelic cannot be used on Canary calls")
            else:
                if dctOptions.birdseed:
                    strNoCall = "-1"
                else:
                    strNoCall = "-1,-1"
                if dctOptions.assume_triallelic:
                    fHWE = open(dctOptions.output + ".hwe", "w")
                    print >> fHWE, "\t".join(["probe"] + [strTriallelicGenotypeClasses, "chi-squared", "p-value", "0_freq", "A_freq", "B_freq"])
        
        strProbe = lstFields[0]
        if len(lstCalls) != iNumSamples:
            raise Exception("Wrong number of calls on this line: " + strLine)
        strConfs = fConfs.readline()
        lstConfs = strConfs.split()
        if strProbe != lstConfs[0]:
            raise Exception("Probe name mismatch between calls and confs: " + strProbe + "; " + lstConfs[0])
        lstConfs = [convertConfidenceToFloat(val) for val in lstConfs[1:]]
        if len(lstConfs) != iNumSamples:
            raise Exception("Wrong number of confidences on this line: " + strConfs)
        for i, fConf in enumerate(lstConfs):
            if fConf > dctOptions.threshold:
                lstCalls[i] = strNoCall

        # 0th index is female
        tupUsualCopiesByGender = dctSpecialProbes.get(strProbe, (2,2))
        
        if bIsCanaryCall:
            clsCall = CanaryCall
        elif dctOptions.birdseed:
            clsCall = BirdseedCall
        else:
            clsCall = LarryBirdCall

        try:
            lstObjCalls = [clsCall(strCall, tupUsualCopiesByGender[lstGenders[i]]) for i, strCall in enumerate(lstCalls)]
        except:
            print >> sys.stderr, "Error constructing call objects for probe:", strProbe, "; sample index", i
            raise

        bTriallelic = dctOptions.assume_triallelic and \
                          isTriallelic(lstPed, lstObjCalls, tupUsualCopiesByGender, clsCall.noCall())
        lstChildrenWithErrors = mendelCheck(lstPed, lstObjCalls, tupUsualCopiesByGender, clsCall.noCall(), dctOptions.assume_triallelic)

        for tupError in lstChildrenWithErrors:
            # Get family and individual ID
            tupPed = lstPed[tupError[0]]
            lstOutput = [str(val) for val in tupPed[:iPATERNAL_ID_INDEX] + [strProbe] + list(tupUsualCopiesByGender) + list(tupError)]
            print >> fMendel, "\t".join(lstOutput)
            lstErrorsPerSample[tupError[0]] += 1

        print >> fLMendel, strProbe, len(lstChildrenWithErrors)

        if bTriallelic:
            tupHWE = hardy_weinberg(lstPed, lstObjCalls, tupUsualCopiesByGender)
            if tupHWE is not None:
                print >>fHWE, "\t".join([strProbe] + [str(val) for val in tupHWE])

    fMendel.close()
    fLMendel.close()
    if fHWE is not None:
        fHWE.close()

    fIMendel = open(dctOptions.output + ".imendel", "w")
    print >> fIMendel, "\t".join(["FID", "KID", "NumErrors"])
    for i, iNumErrors in enumerate(lstErrorsPerSample):
        # Get family and individual ID
        tupPed = lstPed[i]
        print >> fIMendel, "\t".join(tupPed[:iPATERNAL_ID_INDEX] + [str(iNumErrors)])
    fIMendel.close()
        
if __name__ == "__main__":
    sys.exit(main())
    
