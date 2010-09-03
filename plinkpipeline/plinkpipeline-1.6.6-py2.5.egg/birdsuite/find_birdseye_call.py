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

Find the Birdseye/Canary call that was used in determining the copy number for a SNP & sample.
The output is in this form:
FamilyID<tab>IndividualID<tab>SNP<tab>position<tab>Birdseye/Canary call
"""
from __future__ import division
import bisect
import optparse
import sys

from mpgutils import utils

lstRequiredOptions=["sample_snp", "snp_locus", "tfam", "calls"]

def load_tfam(strTFAM):
    """Return a dictionary in which the key is (family ID, individual ID), and the value is 0-based index"""
    lstTFAM = utils.load_tfam(strTFAM)
    dctRet = {}
    for i, tup in enumerate(lstTFAM):
        dctRet[(tup[utils.iTFAM_FAMILY_ID_INDEX], tup[utils.iTFAM_INDIVIDUAL_ID_INDEX])] = i
    return dctRet

def load_snp_locus(strSnpLocus):
    """Return a dictionary with key = SNP name and value = (iChromosome, iPosition)"""
    dctRet = {}
    for lstFields in utils.iterateWhitespaceDelimitedFile(strSnpLocus, iNumFieldsExpected=7):
        strSNP = lstFields[0]
        iChr = int(utils.convertChromosomeStr(lstFields[1]))
        iPosition = int(lstFields[2])
        dctRet[strSNP] = (iChr, iPosition)

    return dctRet

def load_birdseye_canary_calls(strCalls):
    """Returns a list with an element for each sample (0-based).  Each element is a list
    for each chromosome (1-based).  The per-chromosome list contains tuples: (iStart,
    iEnd, lstBirdseyeCanaryCallFields)"""
    lstRet = []
    for lstFields in utils.iterateWhitespaceDelimitedFile(strCalls):
        iSampleNum = int(lstFields[0]) - 1
        iNumCopies = int(lstFields[1])
        iChromosome = int(lstFields[2])
        iStart = int(lstFields[3])
        iEnd = int(lstFields[4])
        for i in xrange(len(lstRet), iSampleNum + 1):
            lstRet.append([])
        lstThisSample = lstRet[iSampleNum]
        for i in xrange(len(lstThisSample), iChromosome + 1):
            lstThisSample.append([])
        lstThisChromosome = lstThisSample[iChromosome]
        lstThisChromosome.append((iStart, iEnd, lstFields))

    return lstRet
        

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--sample_snp",
                      help="""(Required) Find the Birdseye call that produced the CN used to call this sample and SNP.
The first column of this file is Family ID, second column is Individual ID, third column is SNP, and the rest of the
columns are ignored.  This is the format of the *.mendel file produced by mendel_check.py.""")
    parser.add_option("--snp_locus",
                      help="""(Required) Locus for each SNP.""")
    parser.add_option("--tfam",
                      help="""(Required) Used to determine the positional index of each individual.""")
    parser.add_option("--calls",
                      help="""(Required) Birdseye calls.  These are actually a combination of Birdseye and Canary calls,
merged into the same format.""")
    parser.add_option("-o", "--output",
                      help="""Where to write the output.  Default: stdout.""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    dctTFAM = load_tfam(dctOptions.tfam)
    dctSNPLocus = load_snp_locus(dctOptions.snp_locus)
    lstBirdseyeCalls = load_birdseye_canary_calls(dctOptions.calls)

    if dctOptions.output is None:
        fOut = sys.stdout
    else:
        fOut = open(dctOptions.output, "w")

    for lstFields in utils.iterateWhitespaceDelimitedFile(dctOptions.sample_snp):
        strFamilyID = lstFields[0]
        strIndividualID = lstFields[1]
        strSNP = lstFields[2]
        iSampleNum = dctTFAM[(strFamilyID, strIndividualID)]
        (iChromosome, iPosition) = dctSNPLocus[strSNP]
        lstOutputFields = lstFields[:3] + [str(iPosition)]

        lstCallsForThisChromosome = lstBirdseyeCalls[iSampleNum][iChromosome]
        tupSearch = (iPosition, sys.maxint, None)
        iBisect = bisect.bisect_right(lstCallsForThisChromosome, tupSearch)
        if iBisect >= len(lstCallsForThisChromosome):
            print >>fOut, "\t".join(lstOutputFields)
        else:
            if iBisect > 0:
                iBisect -= 1
            assert(lstCallsForThisChromosome[iBisect][0] <= iPosition)
            if lstCallsForThisChromosome[iBisect][1] >= iPosition:
                print >>fOut, "\t".join(lstOutputFields + lstCallsForThisChromosome[iBisect][2])
            else:
                print >>fOut, "\t".join(lstOutputFields)

    if dctOptions.output is not None:
        fOut.close()

if __name__ == "__main__":
    sys.exit(main())
    
