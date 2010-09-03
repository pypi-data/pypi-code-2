#!/usr/bin/env python
"""
usage: %prog [options] <CNsummaries> <CNclusters>

Read CN summaries file, and write CN clusters.
"""
import fileinput
import math
import optparse
import sys

from mpgutils import utils

# Use alternate variance calculation if fewer samples than this
iMIN_SAMPLES1=4
iMIN_SAMPLES2=10

def mean(values):
    x = 0
    for i in values:
        x += i
    return x / len(values)

def trimmean(values, pct=0.8):
    n = len(values)
    x = 0
    leaveout = int((1-pct)/2 * n)
    for i in values[leaveout:(n-leaveout)]:
        x += i
    return x / (n - 2*leaveout)

def var(values):
    avg = mean(values)
    x = 0
    for i in values:
        x += (i-avg)**2
    return x / len(values)

def robustvar(values):
    leaveout = int(.25 * len(values))
    return (0.7413 * (values[leaveout] - values[(len(values)-leaveout-1)]))**2

def parseExclusions(strExclusions, bIncludeSNPs=True, bIncludeCNs=True):
    assert(bIncludeSNPs or bIncludeCNs)
    fIn = fileinput.FileInput([strExclusions])
    # skip header
    for strLine in fIn:
        if strLine.startswith("probeset_id"):
            break
    dctRet = {}
    for strLine in fIn:
        lstFields = strLine.split()
        if len(lstFields) != 2:
            utils.raiseExceptionWithFileInput(fIn, "Exclusions file", "Wrong number of fields")
        strProbe = lstFields[0]
        if not bIncludeCNs and strProbe.startswith("CN"):
            continue
        if not bIncludeSNPs and not strProbe.startswith("CN"):
            continue
        lstExclusions = [int(strVal) for strVal in lstFields[1].split(",")]
        dctRet[strProbe] = lstExclusions
    return dctRet
        
    
def doIt(strCNSummaries, strCNClusters, bExpectHeader=False, dctExclusions=None, lstSampleIndices=None):
    try:
        infile = open(strCNSummaries,'r')
    except IOError:
        print 'Can\'t open file for reading.'
        sys.exit(0)

    if lstSampleIndices is None:
        lstSampleIndices = []
            
    try:
        outfile = open(strCNClusters,'w')
    except IOError:
        print 'Can\'t open file for writing.'
        infile.close()
        sys.exit(0)

    if bExpectHeader:
        # skip header
        for strLine in infile:
            if strLine.startswith("probeset_id"):
                break
    for line in infile:
        values = line.split()
        strProbe = values[0]
        if(len(lstSampleIndices)==0 or (values[1]!="X" and values[1]!="23" and values[1]!="Y" and values[1]!="24")):
            values2 = values[4:]
            if dctExclusions is not None:
                if strProbe in dctExclusions:
                    lstExclusions = dctExclusions[strProbe]
                    if len(lstExclusions) < len(values2):
                        # Don't exclude any if all would be excluded.
                        # Iterate backward so as to not get indices confused.
                        for i in xrange(len(lstExclusions) - 1, -1, -1):
                            del values2[lstExclusions[i]]
                    else:
                        # If no non-excluded samples, make 0, 1 and 2 clusters identical
                        print >> outfile, strProbe + ";1 1;1 1;1 1"
                        continue
        else:
            values2 = []
            for i in lstSampleIndices:
                values2.append(values[i+4])
        for i in range(len(values2)):
            values2[i] = float(values2[i])
        values2.sort()
        mean2 = trimmean(values2)
        if len(values2) >= iMIN_SAMPLES2:
            var2 = robustvar(values2)
        elif len(values2) >= iMIN_SAMPLES1:
            var2 = var(values2)
        else:
            var2 = math.pow(31+0.075*mean2, 2)
        if(values[1]=="Y" or values[1]=="24"):
            mean1 = mean2
            var1 = var2
            mean2 = (mean1 - 41.5529)/0.646
            var2 = var1 / 0.9
            mean0 = mean1 - (0.354*mean2 - 41.5529)/0.75
            var0 = var1 * 0.9
        else:
            mean1 = mean2 - (0.354*mean2 - 41.5529)
            mean0 = mean1 - (0.354*mean2 - 41.5529)/0.75
            var1 = var2 * 0.9
            var0 = var1 * 0.9
        outfile.write(strProbe+";"+str(mean0)+" "+str(var0)+";"+str(mean1)+" "+str(var1)+";"+str(mean2)+" "+str(var2)+"\n")

    infile.close()
    outfile.close()
    

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--header", default=False, action="store_true",
                      help="""Expected a header line in CN summary file.  Default: %default""")
    
    parser.add_option("--exclusions", 
                      help="""File containing CN/sample pairs that should not be included in CN cluster creation.""")
    
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) > 3:
        strSamples = lstArgs[3]
    else:
        strSamples = None

    if dctOptions.exclusions is not None:
        dctExclusions = parseExclusions(dctOptions.exclusions, bIncludeSNPs=False)
    else:
        dctExclusions = None
    doIt(lstArgs[1], lstArgs[2],
         strSamples=strSamples, bExpectHeader=dctOptions.header, dctExclusions=dctExclusions)

if __name__ == "__main__":
    sys.exit(main())
    
