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

Run apt-geno-qc on the specified cel files, and produce a list of cel files that
pass mini-DM threshold, and a corresponding gender file."""

from __future__ import division
import optparse
import os
import sys
import tempfile

from mpgutils import utils

lstRequiredOptions=["cel_files_out"]

strMETADATA_DIR="/humgen/affy_info/GAPProduction/exp"

strEXECUTABLE_DIR="/fg/software/Affymetrix/GAPProduction/prod"

strDEFAULT_CHIP_TYPE = "GenomeWideSNP_6"

fMINI_DM_THRESHOLD=0.86

def readCelFilesList(strPath):
    fIn = open(strPath)
    lstRet = [strLine.rstrip() for strLine in fIn if not strLine.startswith("cel_files")]
    fIn.close()
    return lstRet

def parseAptGenoQcOutput(strAptGenoQcOutPath, fThreshold, bStrict):
    """Returns a list of tuples (boolean, int) where the first value is true
    if the sample passed mini-DM threshold, and the second is 0 for female, 1 for male, 2 for unknown.
    """
    if bStrict:
        iUpperMiniDMIndex = 5
    else:
        iUpperMiniDMIndex = 2
        
    lstRet = []
    fIn = open(strAptGenoQcOutPath)
    if not fIn.readline().startswith("cel_files"):
        raise Exception("Strange header in apt-geno-qc output file " + strAptGenoQcOutPath)
    for strLine in fIn:
        lstFields = strLine.split()
        lstMiniDM = [float(strVal) for strVal in lstFields[1:iUpperMiniDMIndex]]
        bPassed = True
        for fScore in lstMiniDM:
            if fScore > 1.0:
                raise Exception("Strange mini-DM score: " + str(fScore) + " on line: " + strLine)
            if fScore < fThreshold:
                bPassed = False
                break
        strGender = lstFields[8]
        if strGender == "female":
            iGender = 0
        elif strGender == "male":
            iGender = 1
        else:
            iGender = 2

        lstRet.append((bPassed, iGender))
        
    return lstRet
                     
    

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("--cel_files_out", 
                      help="(Required) Where to write the list of cel files that pass mini-DM threshold.")
    parser.add_option("--gender_out", 
                      help="If present, write the genders for the cel files that pass mini-DM threshold to this file.")
    parser.add_option("--map_out", 
                      help="If present, write a file that maps cel file name to gender.")
    parser.add_option("--chip_type", default=strDEFAULT_CHIP_TYPE,
                      help="""Which chip type the cel files are. Default: %default""")
    parser.add_option("--metadata_dir", default=strMETADATA_DIR,
                      help="Location of metadata files.  Default: %default")
    parser.add_option("--exe_dir", default=strEXECUTABLE_DIR,
                      help="Location of executable files.  Default: %default")
    parser.add_option("--cel_files", 
                      help="""Text file specifying cel files to process, one per line
the first line being 'cel_files'. Default: get cel files from command line.""")
    parser.add_option("-t", "--threshold", default=fMINI_DM_THRESHOLD, type="float",
                      help="Mini-DM threshold.  Default: %default")
    parser.add_option("-s", "--strict", default=False, action="store_true",
                      help="Require that all mini-DM scores are above threshold, instead of just the 'all' score.  Default: %default")
    parser.add_option("--force", default=False, action="store_true",
                      help="Pass --force option to apt-geno-qc.  Default: %default")
    parser.add_option("-d", "--debug", default=False, action="store_true",
                      help="Do not delete apt-geno-qc output file.")
    parser.add_option("-o", "--output",
                      help="""Where to write the apt-geno-qc output file.  By default this is written to a temp file
and deleted after information if extracted from it.  Use this option to place it where you like.""")
    dctOptions, lstArgs = parser.parse_args(argv)

    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if dctOptions.cel_files is not None and len(lstArgs) > 1:
        print >> sys.stderr, "ERROR: --cel-files option and putting cel file on command line are mutually exclusive."
        parser.print_help()
        return 1

    if dctOptions.cel_files is None and len(lstArgs) == 1:
        print >> sys.stderr, "ERROR: No cel files specified.  They must either be specified on the command line, or via the --cel-files option."
        parser.print_help()
        return 1

    # 2nd element of tuple is the filename
    if dctOptions.output is not None:
        strAptGenoQcOutPath = dctOptions.output
    else:
        strAptGenoQcOutPath = tempfile.mkstemp(".apt-geno-qc-out")[1]

    if dctOptions.cel_files is not None:
        lstCelFiles = readCelFilesList(dctOptions.cel_files)
    else:
        lstCelFiles = lstArgs[1:]
    
    lstAptGenoQcArgs = [os.path.join(dctOptions.exe_dir, "apt-geno-qc"),
               "-c", os.path.join(dctOptions.metadata_dir, dctOptions.chip_type + ".cdf"),
               "-q", os.path.join(dctOptions.metadata_dir, dctOptions.chip_type + ".qcc"),
               "-a", os.path.join(dctOptions.metadata_dir, dctOptions.chip_type + ".apt-geno-qc.qca"),
               "--chrX-probes", os.path.join(dctOptions.metadata_dir, dctOptions.chip_type + "_gender_chrx_probes.txt"),
               "--chrY-probes", os.path.join(dctOptions.metadata_dir, dctOptions.chip_type + "_gender_chry_probes.txt"),
               "--out-file", strAptGenoQcOutPath]
    if dctOptions.force:
        lstAptGenoQcArgs.append("--force")
        
    lstAptGenoQcArgs += lstCelFiles

    utils.check_call(lstAptGenoQcArgs, True)

    lstResults = parseAptGenoQcOutput(strAptGenoQcOutPath, dctOptions.threshold, dctOptions.strict)
    assert(len(lstCelFiles) == len(lstResults))

    fCelFilesOut = open(dctOptions.cel_files_out, "w")
    print >> fCelFilesOut, "cel_files"
    if dctOptions.gender_out is not None:
        fGenderOut = open(dctOptions.gender_out, "w")
        print >> fGenderOut, "gender"
    else:
        fGenderOut = None

    if dctOptions.map_out is not None:
        fMapOut = open(dctOptions.map_out, "w")
        print >> fMapOut, "cel_files\tgender"
    else:
        fMapOut = None
    
    for i, strCelFile in enumerate(lstCelFiles):
        if lstResults[i][0]:
            print >> fCelFilesOut, os.path.abspath(strCelFile)
            if fGenderOut is not None:
                print >> fGenderOut, lstResults[i][1]
            if fMapOut is not None:
                print >> fMapOut, "\t".join([os.path.abspath(strCelFile), str(lstResults[i][1])])

    fCelFilesOut.close()
    if fGenderOut is not None:
        fGenderOut.close()
    if fMapOut is not None:
        fMapOut.close()
    
    if not dctOptions.debug and dctOptions.output is None:
        os.unlink(strAptGenoQcOutPath)
        
if __name__ == "__main__":
    sys.exit(main())
    
