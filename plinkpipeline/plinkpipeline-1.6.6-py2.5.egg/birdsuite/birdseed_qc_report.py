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

Produce an HTML summary report based on the output of mendel_check.py run on birdseed or larry_bird calls.
Reads the files INPUTROOT.{lmendel,imendel,hwe}
and produces an HTML summary, which is written to OUTPUTFILE."""

from __future__ import division
import optparse
import sys

import bucketize_html
import bucketize_results
import make_html_table
from mpgutils import utils

lstRequiredOptions = ["root", "output"]

def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option('--root', 
                      help='(Required) This is prepended to the various file extensions to find the input files.')
    parser.add_option('-o', '--output', 
                      help='(Required) Where to write the HTML output.')
    parser.add_option('-t', '--title', default="Birdseed QC Report",
                     help="HTML title.  Default: %default.")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    docBuilder = make_html_table.HTMLDocBuilder(dctOptions.title)

    fHWE = open(dctOptions.root + ".hwe")
    strTitle = "Hardy-Weinberg p-value  by SNP"
    table = bucketize_html.doit(strTitle,
                                3,
                                fHWE,
                                [0.1, 0.01, 0.001, 0.0001],
                                strFirstHeader='p-value ')
    fHWE.close()
    docBuilder.addBodyElementAndTOCEntry(table, strTitle)

    fLBIMendel = open(dctOptions.root + ".imendel")
    strTitle = 'Mendel errors in individuals'
    table = bucketize_html.doit(strTitle,
                                2,
                                fLBIMendel,
                                [0, 100, 200, 500, 600, 700, 800, 900, 1000, 1250, 1500, 1750, 2000, 3000, 4000, 5000],
                                strFirstHeader='Errors in individual')
    fLBIMendel.close()
    docBuilder.addBodyElementAndTOCEntry(table, strTitle)

    fLBLMendel = open(dctOptions.root + ".lmendel")
    strTitle = 'Mendel errors in SNPs'
    rowAccumulator = bucketize_results.RowAccumulator([0,1,2,3,4,5,6,7,8,9,10,20,50,100,150,200], 1)
    bucketAccumulator = bucketize_results.BucketAccumulator(strFirstHeader="Errors in SNP", bCumValuePercent=True)
    rowAccumulator.accumulateRowsAndBuckets(bucketAccumulator, fLBLMendel)
    lstFooters = [("Average", "%.3f" % rowAccumulator.getAverage()),
                  ("Total", rowAccumulator.fCumulativeVal)]
    table = make_html_table.makeTableElement(strTitle,
                                             bucketAccumulator.getHeaderFields(),
                                             bucketAccumulator.lstResults,
                                             lstFooters)
    fLBLMendel.close()
    docBuilder.addBodyElementAndTOCEntry(table, strTitle)
    
    docBuilder.writeToFile(dctOptions.output)
    

if __name__ == "__main__":
    sys.exit(main())
    
