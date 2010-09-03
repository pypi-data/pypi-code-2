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

Compare two sets of call and confidence files, and report the amount of agreement."""

from __future__ import division
import optparse
import sys

import birdseed.call_confidence_parser
from mpgutils import utils

lstRequiredOptions = ["calls_a", "confs_a", "calls_b", "confs_b"]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--calls_a", 
                      help="""(Required) First calls file.""")
    parser.add_option("--confs_a", 
                      help="""(Required) Confidences file that is the partner of first calls file.""")
    parser.add_option("--calls_b", 
                      help="""(Required) Second calls file.""")
    parser.add_option("--confs_b", 
                      help="""(Required) Confidences file that is the partner of second calls file.""")

    parser.add_option("--snps", 
                      help="""Only consider SNPs listed in this file.""")
    parser.add_option("--threshold", type="float", default="0.1",
                      help="""Call with confidence >= this value is not confident.  Default: %default""")
    parser.add_option("--changed_snps", 
                      help="""Write a list of SNPs with differences to this file.""")
    parser.add_option("--conf_significance", type="float", default="0.01",
                      help="""Confidences that differ by less than this are considered the same.  Default: %default""")

    dctOptions, lstArgs = parser.parse_args(argv)

    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if len(lstArgs) > 1:
        print >> sys.stderr, "ERROR: Unexpected argument on command line."
        parser.print_help()
        return 1

    calls1 = call_confidence_parser.CallsConfidencesParser(dctOptions.calls_a, dctOptions.confs_a, None).\
             iterateCallsAndConfidences()
    calls2 = call_confidence_parser.CallsConfidencesParser(dctOptions.calls_b, dctOptions.confs_b, None).\
             iterateCallsAndConfidences()
    if dctOptions.snps:
        stSNPs = set([lstFields[0] for lstFields in \
                      utils.iterateWhitespaceDelimitedFile(dctOptions.snps, iNumFieldsExpected=1)])
    else:
        stSNPs = None

    if dctOptions.changed_snps is not None:
        fChangedSNPs = open(dctOptions.changed_snps, "w")
    else: fChangedSNPs = None

    iAgree = 0
    iConfsDisagreeBothConfident = 0
    iConfsDisagreeOneConfident = 0
    iCallsDisagree = 0
    iBothNotConfident = 0
    iOneLBZapped = 0
    
    while True:
        try:
            (strSNP1, lstCalls1, lstConfs1) = calls1.next()
        except StopIteration:
            utils.assertRaises(StopIteration, calls2.next)
            break
        (strSNP2, lstCalls2, lstConfs2) = calls2.next()
        assert(len(lstCalls1) == len(lstCalls2))

        if strSNP1 != strSNP2:
            raise Exception("Calls files have different SNPs: " + strSNP1 + "; " + strSNP2)

        if stSNPs is not None and strSNP1 not in stSNPs:
            continue

        strDiffMsg = ""
        for i in xrange(len(lstCalls1)):
            strCall1 = lstCalls1[i]
            strCall2 = lstCalls2[i]

            bConfidencesDifferent = abs(lstConfs1[i] - lstConfs2[i]) > dctOptions.conf_significance
            b1Confident = lstConfs1[i] <= dctOptions.threshold
            b2Confident = lstConfs2[i] <= dctOptions.threshold
            
            if not b1Confident and not b2Confident:
                iBothNotConfident += 1
            elif strCall1 == strCall2:
                if not b1Confident or not b2Confident:
                    iConfsDisagreeOneConfident += 1
                    strDiffMsg += "; %d: One not confident: Confs %f %f" % (i, lstConfs1[i], lstConfs2[i])
                elif bConfidencesDifferent:
                    iConfsDisagreeBothConfident += 1
                    strDiffMsg += "; %d: Both confident: Confs %f %f" % (i, lstConfs1[i], lstConfs2[i])
                else: iAgree += 1
            else:
                if (strCall1 == '-1' and lstConfs1[i] == 1) or \
                   (strCall2 == '-1' and lstConfs2[i] == 1):
                    iOneLBZapped += 1
                    strDiffMsg += "; %d LB no-call %s:%f %s:%f" % \
                                  (i, lstCalls1[i], lstConfs1[i], lstCalls2[i], lstConfs2[i])
                else:
                    iCallsDisagree += 1
                    strDiffMsg += "; %d: Calls %s %s" % (i, lstCalls1[i], lstCalls2[i])
                
        if len(strDiffMsg) > 0 and fChangedSNPs is not None:
            print >> fChangedSNPs, strSNP1, strDiffMsg

    if fChangedSNPs is not None:
        fChangedSNPs.close()
                
    print "Agree:", iAgree
    print "Calls disagree:", iCallsDisagree
    print "Confs disagree both confident:", iConfsDisagreeBothConfident
    print "Confs disagree one confident:", iConfsDisagreeOneConfident
    print "Both not confident:", iBothNotConfident
    print "Larry bird no-call:", iOneLBZapped
    

if __name__ == "__main__":
    sys.exit(main())
    
