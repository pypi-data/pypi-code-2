#!/usr/bin/env python
import optparse
import sys, os, getopt, re
from mpgutils import utils

def main(argv = None):  
    
    lstRequiredOptions=["metadir", "outputdir"]
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-x", "--metadir",
                      help="(Required) Meta directory holding CNV data")
    #OPTIONAL
    parser.add_option("-d", "--outputdir",
                      help ="Define the directory for output files")
    parser.add_option("-n", "--outputname", default="Output",
                      help="Define the file name root for the output files")
    parser.add_option("-c", "--chip", default=6,
                      help="Chip type")
    parser.add_option("-b", "--build", default=18,
                      help="Human Genome Build")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
    #VALIDATE PATHS
    lstOptionsToCheck = ['outputdir', 'metadir']
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    #LOOK FOR METADATA
    meta_name = str(dctOptions.chip) + "[.]hg" + str(dctOptions.build) + "[.]cnv_defs"
    pattern = re.compile(meta_name, re.IGNORECASE)
    map_files = utils.findFiles(dctOptions.metadir, pattern)
    if map_files:
        MapFile = open(map_files[0])
    else:
        print "\t****No CNV Definitions **** " + str(dctOptions.metadir) + "  -- Chip: " + str(dctOptions.chip) + " -- Build: " + str(dctOptions.build)
        sys.exit(2)
    
    #FILE OUT
    fOut = open(os.path.join(dctOptions.outputdir, dctOptions.outputname + ".canary.map"), "w")
    for strLine in MapFile:
        Fields=strLine.split() 
        if Fields[0] == "cnp_id":
            continue
        fOut.write(("%s\t%s\t0\t%s\n") % (Fields[1],Fields[0],(((int(Fields[3])-int(Fields[2]))/2) + int(Fields[2]))))
    print "Finished -- canary_map.Py\n"
    
if __name__ == "__main__":
    main()