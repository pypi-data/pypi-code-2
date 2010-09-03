from mpgutils import utils

class Filter(object):
    def __init__(self, strGenderFile, strSpecialSNPsFile):
        self._lstGenders = utils.loadGenders(strGenderFile)
        self._dctSpecialSNPs = {}
        utils.loadSpecialProbes(self._dctSpecialSNPs, strSpecialSNPsFile)
        self.lstExpectedSNPs = []
        self.lstUnexpectedSNPs = []

    def numSamples(self):
        return len(self._lstGenders)
    
    def filterCalls(self, strSNP, lstCalls):

        # tuple of (expectedFemaleCount, expectedMaleCount)
        # if SNP is not in dictionary, it is diploid
        #Returns a tup with (female,male)
        tupExpectedCount = self._dctSpecialSNPs.get(strSNP, (2,2))

        lstOutput = [None] * len(lstCalls)

        # This is just for speed.  Avoids one dereference in loop
        lstGenders = self._lstGenders

        #iB == male expected
        #iA == female expected
        bAnyCallZapped = False
        for i, strCall in enumerate(lstCalls):
            if strCall is None:
                iA = -1
                iB = -1
            else: (iA, iB) = [int(strVal) for strVal in strCall.split(",")]
            if iA == -1:
                if iB != -1:
                    raise Exception("Strange call (" + strCall + ") for SNP " + strSNP)
                lstOutput[i] = -1
            elif tupExpectedCount[lstGenders[i]] == 0:
                lstOutput[i] = -1
                bAnyCallZapped = True
            else:
                iTotal = iA + iB
                if iTotal != tupExpectedCount[lstGenders[i]]:
                    lstOutput[i] = -1
                    bAnyCallZapped = True
                else:
                    if iTotal == 2 or iB != 1:
                        lstOutput[i] = iB
                    else:
                        # for haploid B call, emit 2 even though B count is 1
                        lstOutput[i] = 2

        if bAnyCallZapped:
            self.lstUnexpectedSNPs.append(strSNP)
        else:
            self.lstExpectedSNPs.append(strSNP)
            
        return lstOutput