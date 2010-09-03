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

from __future__ import division
import fileinput
import sys

from mpgutils import utils

class CNVDefinition(object):
    def __init__(self, strCNVName, strChrName, iStartPosn, iEndPosn):
        self.strCNVName = strCNVName
        self.strChrName = strChrName
        self.iStartPosn = iStartPosn
        self.iEndPosn = iEndPosn

    def __str__(self):
        return self.strCNVName + " chr" + self.strChrName + " " + str(self.iStartPosn) + ":" + str(self.iEndPosn)

    def length(self):
        return self.iEndPosn - self.iStartPosn + 1
    
def _cmpCNVDefinitionByStart(cnv1, cnv2):
    return cmp(cnv1.iStartPosn, cnv2.iStartPosn)

def _cmpCNVDefinitionByEnd(cnv1, cnv2):
    return cmp(cnv1.iEndPosn, cnv2.iEndPosn)

def _findCNVCandidatesUsingStartPosn(lstCNV, iStartPosn):
    """lstCNV is ordered by start posn.  Return index if the first
    CNV definition that has start posn > iStartPosn."""
    lo = 0
    hi = len(lstCNV)
    while lo < hi:
        mid = (lo+hi)//2
        if iStartPosn < lstCNV[mid].iStartPosn: hi = mid
        else: lo = mid+1
    return lo
    
def _findCNVCandidatesUsingEndPosn(lstCNV, iEndPosn):
    """lstCNV is ordered by end posn.  Return index if the first
    CNV definition that has end posn >= iEndPosn."""
    lo = 0
    hi = len(lstCNV)
    while lo < hi:
        mid = (lo+hi)//2
        if lstCNV[mid].iEndPosn < iEndPosn: lo = mid+1
        else: hi = mid
    return lo
    

class CNVDefinitionCollection(object):
    def __init__(self, strCNVDefsPath):
        # CNVs indexed by name
        self._dctCNVs = {}

        self._fIn = fileinput.FileInput([strCNVDefsPath])
        self._strLine = self._fIn.readline().rstrip("\n")
        lstHeaders = self._strLine.split()
        if lstHeaders != ["cnp_id", "chr", "start", "end"]:
            self._reportError("Unexpected header line in CNV definition file")

        for self._strLine in self._fIn:
            self._strLine = self._strLine.rstrip("\n")
            lstFields = self._strLine.split()
            if len(lstFields) < 4:
                self._reportError("Not enough fields in CNV definition file")
            for i in [1, 2, 3]:
                if not lstFields[i].isdigit():
                    self._reportError("Non-numeric value in column " + str(i))

            if lstFields[0] in self._dctCNVs:
                self._reportError("CNV defined more than once")
            self._dctCNVs[lstFields[0]] = CNVDefinition(lstFields[0], lstFields[1], int(lstFields[2]), int(lstFields[3]))

        self._fIn.close()

        # These are only stored as data members during parsing, so get rid of them when
        # done parsing to avoid confusion.
        del self._fIn
        del self._strLine

        # Group CNVs by chromosome
        dctCNVsByChromosome = {}
        for cnv in self._dctCNVs.values():
            try:
                dctCNVsByChromosome[cnv.strChrName].append(cnv)
            except KeyError:
                    dctCNVsByChromosome[cnv.strChrName] = [cnv]

        # Key = chromosome (string)
        # Value = tup(list of CNVs ordered by startPosn, list of CNVs ordered by endPosn)
        self._dctCNVStartAndEndListsByChromosome = {}
        for strChr, lstCNVs in dctCNVsByChromosome.iteritems():
            lstCNVs.sort(_cmpCNVDefinitionByStart)
            lstCNVsSortedByEnd = lstCNVs[:]
            lstCNVsSortedByEnd.sort(_cmpCNVDefinitionByEnd)
            self._dctCNVStartAndEndListsByChromosome[strChr] = (lstCNVs, lstCNVsSortedByEnd)

    def getCNVsForLocus(self, strChr, iPosn):
        """Return set of CNVs that contain the given locus"""
        #if there are no entries, return length 0 instead of trying to sort (and failing)
        if not self._dctCNVStartAndEndListsByChromosome.has_key(strChr):
            return []
        
        (lstOrderedByStart, lstOrderedByEnd) = self._dctCNVStartAndEndListsByChromosome[strChr]

        # Set of CNVs for this chromosome with iStartPosn <= iPosn
        stCandidatesByStartPosn = set(lstOrderedByStart[:_findCNVCandidatesUsingStartPosn(lstOrderedByStart, iPosn)])

        # Set of CNVs for this chromosome with iEndPosn >= iPosn
        stCandidatesByEndPosn = set(lstOrderedByEnd[_findCNVCandidatesUsingEndPosn(lstOrderedByEnd, iPosn):])

        # CNVs that contain this locus are the intersection of the two sets
        return stCandidatesByStartPosn & stCandidatesByEndPosn

    def getCNV(self, strCNV):
        if strCNV not in self._dctCNVs:
            return None
        return self._dctCNVs[strCNV]

    def _reportError(self, strErrorMessage):
        utils.raiseExceptionWithFileInput(self._fIn, "CNV definition file", strErrorMessage)

def main(argv=None):
    """Just for testing this module"""
    if argv is None:
        argv = sys.argv

    cnvDefs = CNVDefinitionCollection(argv[1])
    while True:
        strLine = raw_input("Enter chromosome number and position separated by space: ")
        strChr, strPosn = strLine.split()
        stCNVs = cnvDefs.getCNVsForLocus(strChr, int(strPosn))
        for cnv in stCNVs:
            print cnv

if __name__ == "__main__":
    sys.exit(main())
    
