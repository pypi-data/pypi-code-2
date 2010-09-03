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
"""usage %prog [options] [cel-files...]

Run birdsuite_qc and then birdsuite.
"""

from __future__ import division
import optparse
import os.path
import sys

from mpgutils import utils

# Edit the line below to suite your installation
strDEFAULT_METADATA_DIR = "/humgen/affy_info/GAPProduction/exp"

lstRequiredOptions = ["basename"]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("--basename", 
                      help="(Required) Used to name all the output files.")
    parser.add_option("--outputDir", default=".",
                      help="Where to write the large volume of output data. Default: current directory")
    parser.add_option("--chipType",  default="GenomeWideSNP_6",
                      help="""Which chip type the cel files are. This is used to select the appropriate metadata files.
Default: %default""")
    parser.add_option("--force", default=False, action="store_true",
                      help="""Passed through to apt-probeset-summarize and apt-geno-qc.""")
    parser.add_option("--genomeBuild", default="hg18",
                      help="What version of locus metadata to use.  Must be one of: ['hg17', 'hg18']. Default: %default")
    parser.add_option("--noLsf", default=False, action="store_true",
                      help="""Do not use LSF to run birdseye jobs.  Run them synchronously instead.  Default: %default""")
    parser.add_option("--lsfQueue", default="birdseed",
                      help="Use given LSF queue for parallelizing birdseye.  Default: %default")
    parser.add_option("--exeDir",
                      help="""Location of Birdsuite executables.  Default: location of this script""")
    parser.add_option("--metadataDir", default=strDEFAULT_METADATA_DIR,
                      help="""Location of Birdsuite metadata.  Default: %default""")
    parser.add_option("--miniDMThreshold", default=0.86, type="float",
                      help="Mini-DM threshold.  Default: %default")
    parser.add_option("--strict", default=False, action="store_true",
                      help="Require that all mini-DM scores are above threshold, instead of just the 'all' score.  Default: %default")
    parser.add_option("--celFiles", 
                      help="""Text file specifying cel files to process, one per line
the first line being 'cel_files'. Default: get cel files from command line.""")

    dctOptions, lstArgs = parser.parse_args(argv)
    
                      
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    if dctOptions.celFiles is not None and len(lstArgs) > 1:
        print >> sys.stderr, "ERROR: --cel-files option and putting cel file on command line are mutually exclusive."
        parser.print_help()
        return 1

    if dctOptions.celFiles is None and len(lstArgs) == 1:
        print >> sys.stderr, "ERROR: No cel files specified.  They must either be specified on the command line, or via the --cel-files option."
        parser.print_help()
        return 1

    if dctOptions.exeDir is None:
        dctOptions.exeDir = os.path.dirname(lstArgs[0])

    strPassingCelFilesPath = os.path.join(dctOptions.outputDir, dctOptions.basename + ".passed_miniDM.cels")
    strPassingGenderPath =os.path.join(dctOptions.outputDir, dctOptions.basename + ".passed_miniDM.gender")
    
    lstQCArgs = [os.path.join(dctOptions.exeDir, "birdsuite_qc.py"),
               "--cel_files_out", strPassingCelFilesPath,
               "--gender_out", strPassingGenderPath,
               "--chip_type", dctOptions.chipType,
               "--metadata_dir", dctOptions.metadataDir,
               "--exe_dir", dctOptions.exeDir,
               "--threshold", str(dctOptions.miniDMThreshold)]
    if dctOptions.strict:
        lstQCArgs.append("--strict")
    if dctOptions.force:
        lstQCArgs.append("--force")
    if dctOptions.celFiles:
        lstQCArgs += ["--cel_files", dctOptions.celFiles]
    else:
        lstQCArgs += lstArgs[1:]

    utils.check_call(lstQCArgs, True)

    lstBirdsuiteArgs = [os.path.join(dctOptions.exeDir, "birdsuite.sh"),
                        "--basename", dctOptions.basename,
                        "--chipType", dctOptions.chipType,
                        "--outputDir", dctOptions.outputDir,
                        "--genderFile", strPassingGenderPath,
                        "--genomeBuild", dctOptions.genomeBuild,
                        "--metadataDir", dctOptions.metadataDir,
                        "--exeDir", dctOptions.exeDir,
                        "--celFiles", strPassingCelFilesPath]
    if dctOptions.force:
        lstBirdsuiteArgs.append("--force")
    if dctOptions.noLsf:
        lstBirdsuiteArgs.append("--noLsf")
    if dctOptions.lsfQueue:
        lstBirdsuiteArgs += ["--lsfQueue", dctOptions.lsfQueue]

    utils.check_call(lstBirdsuiteArgs, True)

                        
    
    
               
if __name__ == "__main__":
    sys.exit(main())
    
