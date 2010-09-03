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
"""usage %prog [options] cel-files...

Generate non-normalized allele summaries for the cel files, and then for each cel file
bin the intensities by sty fragment length and nsp fragment length."""

from __future__ import division
import optparse
import os
import sys

from mpgutils import utils

strALLELE_SUMMARY_FILE="pm-only.plier.expr.summary.txt"
strMETADATA_DIR = "/humgen/affy_info/GAPProduction"

# Plus one for 0 length
iNUM_BUCKETS = 10

lstChipTypes = ["GenomeWideSNP_6", "BI_SNP"]

dctAnnotationFile = {"GenomeWideSNP_6": os.path.join(strMETADATA_DIR, "GenomeWideSNP_6.na22.annot.csv"),
                     "BI_SNP": os.path.join(strMETADATA_DIR, "GenomeWideSNP_5.na23.annot.csv")
                     }

lstRequiredOptions = ["chip_type"]

def convertFragmentLength(strFragmentLength):
    if strFragmentLength == "---":
        return 0
    return int(strFragmentLength)

def calcBucketNumber(iLength, fBucketSize):
    if iLength == 0:
        return 0
    iBucketNumber = int((iLength // fBucketSize) + 1)
    if iBucketNumber > iNUM_BUCKETS:
        iBucketNumber = iNUM_BUCKETS
    return iBucketNumber

class FragmentLengthBucketizer(object):
    def __init__(self, strAnnotationFile):

        # Key is SNP name, value is (nsp frag length, sty frag length)
        self.dctFragmentLengthBySNP = {}
        iMaxNspFragmentLength = 0
        iMaxStyFragmentLength = 0
        for lstFields in utils.parseAnnotationFile(strAnnotationFile):
            strSNP = lstFields[0]
            strFragmentInfo = lstFields[14]
            lstFragmentInfo = strFragmentInfo.split("///")
            if len(lstFragmentInfo) < 2:
                print >> sys.stderr, strSNP, "doesn't have Nsy and Sty fragment lengths"
                continue
            lstFragmentLengths = [strFragmentInfo.split("//")[0].strip() for strFragmentInfo in lstFragmentInfo]
            iNspFragmentLength = convertFragmentLength(lstFragmentLengths[0])
            iStyFragmentLength = convertFragmentLength(lstFragmentLengths[1])
            if iStyFragmentLength > 5000:
                print >> sys.stderr, "Big Sty fragment", strSNP, lstValues
            self.dctFragmentLengthBySNP[strSNP] = (iNspFragmentLength, iStyFragmentLength)
            iMaxNspFragmentLength = max(iMaxNspFragmentLength, iNspFragmentLength)
            iMaxStyFragmentLength = max(iMaxStyFragmentLength, iStyFragmentLength)

        print "Max Nsp fragment:", iMaxNspFragmentLength, "; Max Sty fragment:", iMaxStyFragmentLength
        self.iNspBucketSize = iMaxNspFragmentLength / iNUM_BUCKETS
        self.iStyBucketSize = iMaxStyFragmentLength / iNUM_BUCKETS

    def getBucketNumbers(self, strSNPName):
        """Returns (iNspBucketNumber, iStyBucketNumber), or (None, None) if SNP name is not
        recognized."""
        if not (strSNPName.endswith("-A") or strSNPName.endswith("-B")):
            return (None, None)
        strSNPName = strSNPName[:-2]
        if strSNPName not in self.dctFragmentLengthBySNP:
            return (None, None)
        iNspFragmentLength, iStyFragmentLength = self.dctFragmentLengthBySNP[strSNPName]
        return (calcBucketNumber(iNspFragmentLength, self.iNspBucketSize),
                calcBucketNumber(iStyFragmentLength, self.iStyBucketSize))

def write_table(fIntensityMean, lstBucketCounts, buckets, strSampleName, strOutputDir):
    fOut = open(os.path.join(strOutputDir, strSampleName + ".frag_length_buckets"), "w")
    print >> fOut, "# Rows are Nsp fragment length buckets, columns are Sty fragment length buckets."
    print >> fOut, "# Each cell contains the mean intensity of all the SNPs that fall into that bucket,"
    print >> fOut, "# normalized by the mean intensity of all SNPs in the sample."
    print >> fOut, "\t".join(["bucket_size"] + [str(i) for i in xrange(iNUM_BUCKETS+1)])
    for iRow in xrange(iNUM_BUCKETS+1):
        print >> fOut, "\t".join([str(iRow)] +
                                 [str(buckets[iRow][iCol]/(fIntensityMean*lstBucketCounts[iRow][iCol])) for iCol in xrange(iNUM_BUCKETS+1)])
    fOut.close()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    # only support 6.0 for now
    #parser.add_option(, "--chip_type", choices=lstChipTypes,
    #                  help="""Required.  Must be one of: """ + str(lstChipTypes))
    parser.add_option("-o", "--out_dir", default=".",
                      help="""Where to write output files.  Default: %default""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    dctOptions.chip_type = "GenomeWideSNP_6"
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if len(lstArgs) < 2:
        print >> sys.stderr, "ERROR: At least one cel file must be supplied on the command line."
        parser.print_help()
        return 1

    lstSummarizeArgs = ['/fg/software/Affymetrix/1chip/apt-probeset-summarize.sh',
                        '-a', 'pm-only,plier.optmethod=1,expr.genotype=true',
                        '--cdf-file', os.path.join(strMETADATA_DIR, dctOptions.chip_type + '.cdf'),
                        '-o', dctOptions.out_dir] + \
                        lstArgs[1:]

    utils.check_call(lstSummarizeArgs)

    bucketizer = FragmentLengthBucketizer(dctAnnotationFile[dctOptions.chip_type])

    fIn = open(os.path.join(dctOptions.out_dir, strALLELE_SUMMARY_FILE))
    strHeader = utils.skipHeader(fIn, "probeset_id")
    lstSampleNames = strHeader.split()[1:]
    iNumSamples = len(lstSampleNames)

    # For calculating mean intensity for each sample
    iNumSNPs = 0
    lstAccumulators = [0.0] * iNumSamples

    # Each bucket has Nsp and Sty totals
    buckets = [[[0.0] * (iNUM_BUCKETS + 1) for i in xrange(iNUM_BUCKETS + 1)] for j in xrange(iNumSamples)]
    
    lstBucketCounts = [[0] * (iNUM_BUCKETS + 1) for i in xrange(iNUM_BUCKETS + 1)]

    for strLine in fIn:
        lstFields = strLine.split()
        strSNPName = lstFields[0]
        iNspBucket, iStyBucket = bucketizer.getBucketNumbers(strSNPName)
        if iNspBucket is None:
            assert(iStyBucket is None)
            continue
        iNumSNPs += 1
        lstIntensities = [float(strField) for strField in lstFields[1:]]
        assert(len(lstIntensities) == iNumSamples)

        for i in xrange(iNumSamples):
            lstAccumulators[i] += lstIntensities[i]
            buckets[i][iNspBucket][iStyBucket] += lstIntensities[i]

        lstBucketCounts[iNspBucket][iStyBucket] += 1

    fIn.close()

    # Get mean intensity for each plate
    lstMeans = [fAccumulator / iNumSNPs for fAccumulator in lstAccumulators]

    for i in xrange(iNumSamples):
        write_table(lstMeans[i], lstBucketCounts, buckets[i], lstSampleNames[i], dctOptions.out_dir)
        
    
if __name__ == "__main__":
    sys.exit(main())
    
