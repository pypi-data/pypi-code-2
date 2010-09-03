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
"""usage: %prog [options] --basename BASENAME --gender_file GENDER_FILE

Generate a report file containing various metrics from the birdsuite run.
"""

from __future__ import division
import optparse
import os.path
import sys

import birdsuite.call_confidence_parser as call_confidence_parser
from mpgutils import utils

lstRequiredOptions=["basename", "gender_file"]

def percent(numerator, denominator):
    return float(numerator) / denominator * 100

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-b", "--basename",
                      help="""(Required)  Used to find the input files and to name the output file.""")
    parser.add_option("--gender_file",
                      help="""(Required)  File containing a line for each sample in
the data file. 0=female, 1=male, 2=unknown. This file must have a header line "gender".""")
    parser.add_option("-d", "--dir", default=".",
                      help="Directory where input and output files are located.  Default: current directory.")
    parser.add_option("-t", "--threshold", type="float", default="0.1",
                      help="""Calls with confidence > this are considered no-calls.  Default: %default""")
    parser.add_option("-p", "--per_sample", action="store_true", default=False,
                      help="""Generate a report file per sample, in addition to the report file for all samples.
Each file is named <sample>.report.txt.  Default: %default""")
    parser.add_option("--cn_buckets", type="int", default="20",
                      help="""Have this many buckets for counting CN calls.  Default: %default""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    callParser = call_confidence_parser.CallsConfidencesParser(
        os.path.join(dctOptions.dir, dctOptions.basename + ".larry_bird_calls"),
        os.path.join(dctOptions.dir, dctOptions.basename + ".larry_bird_confs"),
        dctOptions.threshold)

    iNumSamples = len(callParser.lstCELFiles)
    iNumSNPs = 0
    lstCallsPerSample = [0] * iNumSamples
    lstDiallelicBuckets = [[0,0,0] for i in xrange(iNumSamples)]
    # One extra bucket for all calls > largest bucket
    lstCNBuckets = [[0] * (dctOptions.cn_buckets + 1) for i in xrange(iNumSamples)]

    lstGenders = utils.loadGenders(dctOptions.gender_file)
    if len(lstGenders) != iNumSamples:
        raise Exception("Number of samples in gender file does not equal number of samples in calls file.")

    for strSNP, lstCalls in callParser.iterateSNPs():
        if len(lstCalls) != iNumSamples:
            raise Exception("Wrong number of samples on calls for SNP " + strSNP)
        iNumSNPs += 1
        for iSampleNum, strCall in enumerate(lstCalls):
            if strCall is None or strCall == "-1,-1":
                continue
            lstCallsPerSample[iSampleNum] += 1
            lstCounts = strCall.split(",")
            if len(lstCounts) != 2:
                raise Exception("Strange call for SNP " + strSNP + ": " + strCall)
            lstCounts = [int(strCount) for strCount in lstCounts]
            iTotalCount = lstCounts[0] + lstCounts[1]
            if iTotalCount < dctOptions.cn_buckets:
                lstCNBuckets[iSampleNum][iTotalCount] += 1
            else:
                lstCNBuckets[iSampleNum][dctOptions.cn_buckets] += 1
            if iTotalCount == 2:
                # 0 bucket == AA, 1 == AB, 2 == BB, so just use the BB count as the index
                lstDiallelicBuckets[iSampleNum][lstCounts[1]] += 1

    fOut = open(os.path.join(dctOptions.dir, dctOptions.basename + ".report.txt"), "w")
    lstHeaders = ["cel_files", "computed_gender", "call_rate", "AA_percent", "AB_percent", "BB_percent"] + \
                 ["CN" + str(i) + "_percent" for i in xrange(dctOptions.cn_buckets)] + ["CN>=" + str(dctOptions.cn_buckets) + "_percent"]
    
    print >> fOut, "\t".join(lstHeaders)

    for iSampleNum in xrange(iNumSamples):
        lstFields = [callParser.lstCELFiles[iSampleNum], utils.genderToString(lstGenders[iSampleNum]),
                     percent(lstCallsPerSample[iSampleNum], iNumSNPs)]
        for iCount in lstDiallelicBuckets[iSampleNum]:
            lstFields.append(percent(iCount, lstCNBuckets[iSampleNum][2]))
        for iCount in lstCNBuckets[iSampleNum]:
            lstFields.append(percent(iCount, lstCallsPerSample[iSampleNum]))
        lstFields = [str(val) for val in lstFields]
        print >> fOut, "\t".join(lstFields)

        if dctOptions.per_sample:
            strBasename = callParser.lstCELFiles[iSampleNum]
            if strBasename.endswith(".cel") or strBasename.endswith(".CEL"):
                strBasename = strBasename[:-4]
            fPerSample = open(os.path.join(dctOptions.dir,  strBasename + ".birdsuite.rpt"), "w")
            print >> fPerSample, "\t".join(lstHeaders)
            print >> fPerSample, "\t".join(lstFields)
            fPerSample.close()

    fOut.close()
    
if __name__ == "__main__":
    sys.exit(main())
    
