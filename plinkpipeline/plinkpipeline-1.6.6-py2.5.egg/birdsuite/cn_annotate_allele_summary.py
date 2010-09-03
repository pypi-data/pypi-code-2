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
"""%prog [options]

Create a map between Affy probe set name and genomic position.  This can be done for
CNP probes, SNP probesets, or both.  
"""

from __future__ import division
import optparse
import os
import string
import subprocess
import sys

from mpgutils import utils

lstRequiredOptions = ["probe_locus", "summary"]

def mapSNPs(dctOut, strSnpProbeInfoPath):
    fIn = open(strSnpProbeInfoPath)
    for strLine in fIn:
        lstFields = strLine.split()
        dctOut[lstFields[0]] = (utils.convertChromosomeStr(lstFields[1]), lstFields[2])
    fIn.close()

# Headers to emit if not bOmitLocusColumns
lstLocusHeaders = ['chr', 'position', 'probeset_type']
# Indices of locus columns
iStartLocusColumnIndex = 1
iEndLocusColumnIndex = iStartLocusColumnIndex + len(lstLocusHeaders)

class ProbeExtractor(object):
    def __init__(self, strProbeLocusPath, fUnmappedProbesOut,
                 strTempDir=None, bOmitLocusColumns=False):
        self.bOmitLocusColumns = bOmitLocusColumns
        self.fUnmappedProbesOut = fUnmappedProbesOut
        
        self.dctProbeToGenomicPosition = {}

        self.dctProbeToGenomicPosition = utils.loadProbeLocus(strProbeLocusPath)

        if strTempDir is not None:
            self.lstTempDirArgs = ["-T", strTempDir]
        else:
            self.lstTempDirArgs = []
        # Sort numerically on 2nd and 3rd columns.  Last-resort sort column is probeset name (1st column)
        self.procSort = subprocess.Popen(['sort', '--key=2,2n', '--key=3,3n', '--key=1,1'] + self.lstTempDirArgs,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE)

        
    def processSummary(self, strSummaryPath, fOut):
        fIn = open(strSummaryPath)
        for strLine in fIn:
            if strLine.startswith('#'):
                fOut.write(strLine)
            elif  strLine.startswith('probeset_id'):
                lstHeaders = strLine.split()
                lstOutputHeaders = ['probeset_id']
                if not self.bOmitLocusColumns:
                    lstOutputHeaders += lstLocusHeaders
                print >> fOut, "\t".join(lstOutputHeaders +
                                         lstHeaders[1:])
            else:
                break
        fOut.flush()
        
        # Process the first non-header line
        self._processSummaryLine(strLine)

        # Process the rest of non-header line
        for strLine in fIn:
            self._processSummaryLine(strLine)

        fIn.close()

    def writeOutput(self, fOut):
        print >> sys.stderr, "Finishing sorted output."
        self._sloshOutput(fOut, self.procSort)


    def _processSummaryLine(self, strLine):
        lstFields = strLine.split("\t", 1)
        strProbeSetName = lstFields[0]
        if strProbeSetName.endswith('-A') or strProbeSetName.endswith('-B'):
            strProbeSetType = strProbeSetName[-1]
            strProbeSetName = strProbeSetName[:-2]
        else:
            strProbeSetType = "C"
        try:
            tupGenomicPosition = self.dctProbeToGenomicPosition[strProbeSetName]
            lstGenomicPosition = [str(val) for val in tupGenomicPosition]
            strOut = "\t".join(lstFields[0:1] + lstGenomicPosition + [strProbeSetType] + lstFields[1:])
            self.procSort.stdin.write(strOut)
        except KeyError:
            if self.fUnmappedProbesOut is not None:
                self.fUnmappedProbesOut.write(strLine)

    def _sloshOutput(self, fOut, proc):
        # Tell sort subprocess that there is no more input
        # Try closing another way as well since closing the file object doesn't seem to work.
        proc.stdin.flush()
        proc.stdin.close()
        # Write the output
        if self.bOmitLocusColumns:
            for strLine in proc.stdout:
                lstFields = strLine.split()
                del lstFields[iStartLocusColumnIndex:iEndLocusColumnIndex]
                print >> fOut, "\t".join(lstFields)
        else:
            for strLine in proc.stdout:
                fOut.write(strLine)
        if proc.wait() != 0:
            raise Exception("ERROR: %d exit status from sort." % proc.returncode)



def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("--probe_locus", 
                      help="(Required)  SNP and CN probe positions.")
    parser.add_option("--summary", 
                      help="(Required) Input file containing probeset summaries as produced by apt-probeset-summarize.")
    parser.add_option("-o", "--output", dest="output",
                      help="Where to write output.  Default: stdout")
    parser.add_option("-u", "--unmapped-probes-output", dest="unmappedProbesOut",
                      help="""Where to write summaries of probes for which genomic position is not known.
                      Default: Don't write.""")
    parser.add_option("-t", "--tmpdir", dest="tempdir",
                      help="""If /tmp doesn't have enough room to sort, specify a temp directory with more room.""")
    parser.add_option("--omit-locus-columns", dest="omitLocusColumns", action="store_true", default=False,
                      help="""Do not emit the columns with locus or probe type.  If this argument is used,
                      all this program does is sort the input by genomic position.""")
    
    dctOptions, lstArgs = parser.parse_args(argv)

    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if dctOptions.output:
        fOut = open(dctOptions.output, "w")
    else:
        fOut = sys.stdout

    if dctOptions.unmappedProbesOut:
        fUnmappedProbesOut = open(dctOptions.unmappedProbesOut, "w")
    else:
        fUnmappedProbesOut = None
        
    print >> sys.stderr, "Reading probe info files..."
    probeExtractor = ProbeExtractor(dctOptions.probe_locus,
                                    fUnmappedProbesOut,
                                    strTempDir=dctOptions.tempdir,
                                    bOmitLocusColumns=dctOptions.omitLocusColumns)
    print >> sys.stderr, "Read summary file..."
    probeExtractor.processSummary(dctOptions.summary, fOut)
    print >> sys.stderr, "Finishing sort and writing output..."
    probeExtractor.writeOutput(fOut)

    if dctOptions.output:
        fOut.close()

    if fUnmappedProbesOut is not None:
        fUnmappedProbesOut.close()
    
if __name__ == "__main__":
    sys.exit(main())
    
