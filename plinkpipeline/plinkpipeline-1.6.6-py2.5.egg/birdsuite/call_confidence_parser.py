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

from __future__ import division
import sys

class CallsConfidencesParser(object):
    """Parse a calls and confidences file pair.  After initialization, lstCELFiles will contain the CEL file names."""
    def __init__(self, strCallsPath, strConfidencesPath, fThreshold):
        self._strCallsPath = strCallsPath
        self._strConfidencesPath = strConfidencesPath
        self._fThreshold = fThreshold
        self._fCalls = open(strCallsPath)
        self._fConfidences = open(strConfidencesPath)

        strCallsHeader = self._fCalls.readline()
        strConfidencesHeader = self._fConfidences.readline()
        if strCallsHeader != strConfidencesHeader:
            print >> sys.stderr, 'ERROR: Header lines in', strCallsPath, 'and', strConfidencesPath, 'do not agree.'
            return 1

        strCallsHeader = strCallsHeader.rstrip("\n")

        # Ignore the first column, which is "probeset_id"
        self.lstCELFiles = strCallsHeader.split("\t")[1:]

    def iterateCallsAndConfidences(self):
        """For each iteration, returns (strSNP, lstCalls, lstConfs) where lstCalls contains the calls for each
        sample (as strings), and lstConfs contains the confidence for each sample, as a float."""
        
        for iLineNum, strCalls in enumerate(self._fCalls):
            lstCalls = strCalls.rstrip().split("\t")
            lstConfidences = self._fConfidences.readline().rstrip().split("\t")
            if lstCalls[0] != lstConfidences[0]:
                raise Exception("ERROR: SNP mismatch between", self._strCallsPath, "and", self._strConfidencesPath,\
                      "at line", iLineNum+2, ";", lstCalls[0], "!=", lstConfidences[0])

            strSNP = lstCalls[0]
            del lstCalls[0]
            del lstConfidences[0]
            if len(lstCalls) != len(self.lstCELFiles):
                raise Exception("ERROR: Wrong number of values in", self._strCallsPath,":", iLineNum+2,"; Expected", \
                      len(self.lstCELFiles),"but was", len(lstCalls))

            if len(lstConfidences) != len(self.lstCELFiles):
                raise Exception("ERROR: Wrong number of values in", self._strConfidencesPath,":", iLineNum+2,"; Expected", \
                      len(self.lstCELFiles),"but was", len(lstConfidences))
            lstConfidences = [float(val) for val in lstConfidences]
            yield (strSNP, lstCalls, lstConfidences)

        self._fCalls.close()
        self._fConfidences.close()
        

    def iterateSNPs(self):
        """For each iteration, returns (strSNP, lstCalls) where lstCalls contains the call for each
        sample as a string.  If a call is below threshold for a sample, lstCalls[i] is None.
        Else it is '0' for AA, '1' for AB, '2' for BB. -- actually, this can be used for larry_bird calls
        as well.  There are no assumptions about the form of the calls other than that they are whitespace-
        separated."""

        for strSNP, lstCalls, lstConfidences in self.iterateCallsAndConfidences():

            for i in xrange(len(lstCalls)):
                if lstConfidences[i] > self._fThreshold:
                    lstCalls[i] = None

            yield (strSNP, lstCalls)

        
        
