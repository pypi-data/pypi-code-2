#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2008 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage %prog merge_file input_canary_reference_calls > output_canary_reference_calls

Each line in the merge file contains two or more CNP names.
Read the input_canary_reference_calls, and write to stdout a reference calls file that has
the calls for the CNPs from the merge file merged.  The first CNP on each line in the merge
file is used as the output name for the merged CNP.  If the CNPs to be merged have conflicting
calls for a sample, this is replaced with a no-call.  If one has a call and the other a no-call,
the call is kept."""

from __future__ import division
import optparse
import sys

from mpgutils import utils

def mergeCalls(lstOfLsts):
    """If more than one set of calls in list, merge them.  If all the actual calls for a sample agree,
    the output gets that call.  Otherwise, that sample gets a no-call (-1)"""
    if len(lstOfLsts) == 1:
        return lstOfLsts[0]
    
    lstRet = [None] * len(lstOfLsts[0])

    for lst in lstOfLsts:
        assert(len(lst) == len(lstRet))

    for i in xrange(len(lstRet)):
        strValue = "-1"
        for lst in lstOfLsts:
            if lst[i] == "-1":
                continue
            if strValue == "-1":
                strValue = lst[i]
            elif strValue != lst[i]:
                strValue = "-1"
                break
        lstRet[i] = strValue
        
    return lstRet
                        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(__doc__)
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) != 3:
        parser.print_help()
        return 1

    strMergePath = lstArgs[1]
    strReferenceCallPath = lstArgs[2]

    # Map from original name to merged name
    dctMergedCNPNameMap = {}
    for lstFields in utils.iterateWhitespaceDelimitedFile(strMergePath):
        strNewName = lstFields[0]
        for strCNP in lstFields:
            dctMergedCNPNameMap[strCNP] = strNewName

    # Map from CNP name to list of lists of calls
    dctCNPRefCallsAccumulator = {}
    iterCalls = iter(utils.iterateWhitespaceDelimitedFile(strReferenceCallPath, bSkipHeader=False))

    lstHeaders = iterCalls.next()
    print "\t".join(lstHeaders)
    
    while True:
        try:
            lstFields = iterCalls.next()
        except StopIteration: break
        
        strNewName = dctMergedCNPNameMap.get(lstFields[0], lstFields[0])
        lstCalls = lstFields[1:]
        dctCNPRefCallsAccumulator.setdefault(strNewName, []).append(lstCalls)

    lstKeys = dctCNPRefCallsAccumulator.keys()
    lstKeys.sort()
    for strCNP in lstKeys:
        lstCalls = mergeCalls(dctCNPRefCallsAccumulator[strCNP])
        print "\t".join([strCNP] + lstCalls)
    
if __name__ == "__main__":
    sys.exit(main())
    
