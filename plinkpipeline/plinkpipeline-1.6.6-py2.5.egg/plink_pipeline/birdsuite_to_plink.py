#!/usr/bin/env python
from plink_pipeline import create_map, birdseye_to_cnv, canary_merge, canary_to_gvar, fawkes_to_gvar, fawkes_to_diploid, fawkes_merge, make_tped, make_tfam, fam_to_gender
import optparse
import sys
from mpgutils import utils

def main(argv = None): 
    if not argv:
        argv = sys.argv
    
    lstRequiredOptions=["metadir", "plateroot", "familyfile"]
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-p", "--plateroot",
                      help="""(Required) Contains folders with larry-bird style files""")
    parser.add_option("-f", "--familyfile",
                      help="""(Required) PLINK formatted .fam file""")
    parser.add_option("-x", "--metadir",
                      help="(Required) Meta directory holding CNV data")
    #OPTIONAL
    parser.add_option("-d", "--outputdir",
                      help ="Define the directory for output files (If not defined, use working directory)")
    parser.add_option("-m", "--celmap", dest="celmap",
                      help="Cel Map file")
    parser.add_option("-t", "--threshold", default=0.1,
                      help ="define a cutoff for confidence data")
    parser.add_option("-n", "--outputname", default="Output",
                      help="Define the file name of output files (Do not use extensions)")
    parser.add_option("-c", "--chip", default='6',
                      help="Chip Type")
    parser.add_option("-b", "--build", default='18',
                      help="Human Genome Build")
    parser.add_option("-a", "--noallelemap", default=False, action="store_true",
                      help="""Do not convert Probes to Alleles (Default FALSE)""") 
    parser.add_option("-v", "--ignorefam", default=False, action="store_true",
                      help="""Disable pedigree checking (Default FALSE)""") 
    parser.add_option("-r", "--norscoding", default=False, action="store_true",
                      help="""Do not convert SNP id to RS id (Default FALSE)""")
    parser.add_option("--createCNV", default=False, action="store_true",
                      help="""Build Option: Create .cnv output from birdsuite data""") 
    parser.add_option("--createGVAR", default=False, action="store_true",
                      help="""Build Option: Create .gvar output from birdsuite data""") 
    parser.add_option("--createPED", default=False, action="store_true",
                      help="""Build Option: Create .tped output from birdsuite data""") 
#    parser.add_option("--createVCF", default=False, action="store_true",
#                      help="""Build Option: Create .vcf output from birdsuite data""") 
    
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        print "\n\t*** If you do not specify a 'Build Option' ALL will be run ***"
        return 1
        
    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
        
#    CHECK IF USER WANTS GENERIC RUN
    if not (dctOptions.createCNV or dctOptions.createGVAR or dctOptions.createPED):
        setattr(dctOptions, 'createCNV', True)
        setattr(dctOptions, 'createGVAR', True)
        setattr(dctOptions, 'createPED', True)
        
    #VALIDATE PATHS
    lstOptionsToCheck = ['familyfile', 'plateroot', 'metadir', 'outputdir']
    if dctOptions.celmap:
        lstOptionsToCheck.append("celmap")
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    print "\t========================================================="
    print "\t=             BIRDSUITE FORMAT CONVERTER                ="
    print "\t========================================================="
    fawkesismerged = False
    genderismade = False
    
    #VERIFY FAM FILE
    if not dctOptions.ignorefam:
        if not utils.checkFamFile(dctOptions.familyfile, 0.5):
            print "\nWARNING:"
            print "Family file is missing more than 50% phenotypic information"
            print "It is strongly recommended that you provide this information"
            print "\t-To disable this check use --ignorefam\n\n"
            sys.exit(2)
                                
    if dctOptions.createCNV:
        print "\n===== Creating CNV Files ====="
        
        #BIRDSEYE TO CNV
        possible_args = ["plateroot", "outputdir", "familyfile", "celmap", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nBIRDSEYE->CNV:"
        birdseye_to_cnv.main(current_args)
    
    if dctOptions.createGVAR: 
        print "\n===== Creating GVAR Files ====="
        
        #CREATE CANARY MAP
        possible_args = ["metadir", "outputdir", "outputname", "chip", "build"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nCANARY-MAP:"
        create_map.main(current_args)
    
        #CANARY MERGE
        possible_args = ["plateroot", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nCANARY-MERGE:"
        canary_merge.main(current_args)
    
        #CANARY TO GVAR
        possible_args = ["plateroot", "outputdir", "familyfile", "threshold", "celmap", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nCANARY->GVAR:"
        canary_to_gvar.main(current_args)
        
        #MERGE FAWKES DATA
        fawkesismerged = FawkesMerge(fawkesismerged,dctOptions)
        
        #MAKE GENDER FILES
        genderismade = MakeGender(genderismade, dctOptions)
        
        #FAWKES TO GVAR
        possible_args = ["plateroot", "outputdir", "familyfile", "threshold", "celmap", "outputname", "metadir", "noallelemap", "norscoding"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nFAWKES->GVAR:"
        fawkes_to_gvar.main(current_args)
    
    if dctOptions.createPED:
        print "\n====== Creating TPED Files ====="
        
        #MERGE FAWKES DATA
        fawkesismerged = FawkesMerge(fawkesismerged,dctOptions)
        
        #MAKE GENDER FILES
        genderismade = MakeGender(genderismade, dctOptions)
            
        #FAWKES TO DIPLOID
        possible_args = ["plateroot", "metadir", "chip"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nFAWKES->DIPLOID:"
        fawkes_to_diploid.main(current_args)
        
        #MAKE TPED
        possible_args = ["plateroot", "metadir", "chip", "build", "outputdir", "outputname", "threshold"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nMAKE-TPED:"
        make_tped.main(current_args)
        
        #MAKE TFAM
        possible_args = ["plateroot","familyfile", "outputdir", "outputname", "celmap"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nMAKE-TFAM:"
        make_tfam.main(current_args)
        
def FawkesMerge(fawkesismerged, dctOptions):
    
    if not fawkesismerged:
        #FAWKES MERGE
        possible_args = ["plateroot", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nFAWKES-MERGE:"
        fawkes_merge.main(current_args)
        return True
    
def MakeGender(genderismade, dctOptions):
    
    if not genderismade:
        possible_args = ["plateroot", "outputdir", "familyfile", "outputname", "celmap"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\nFAM->GENDER:"
        fam_to_gender.main(current_args)
        return True
        
def MakeArguments(possible_args, dctOptions):
    current_args = []
    for key in possible_args:
        item = getattr(dctOptions, key)
        if not item == None:
            if item == True:
                current_args.append("--" + key)
            elif item == False:
                continue
            else:
                current_args.append("--" + key)
                current_args.append(item)
    return current_args
    
    
if __name__ == "__main__":
    main()  
    
