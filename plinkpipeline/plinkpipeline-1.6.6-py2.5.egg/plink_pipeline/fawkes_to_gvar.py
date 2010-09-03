#!/usr/bin/env python
import optparse
import sys
import os
import getopt
import re
import shutil
from mpgutils import utils
#import DiploidCallsFilter

#GLOBALS
dctIndivMap = {}
dctCallFile = {}
output_root = ""
output_name = "Output"
    
def main(argv = None):    
    #OPTION PARSING!
    global output_root, output_name
    
    if argv is None:
        argv = sys.argv
    lstRequiredOptions=["familyfile", "plateroot", "metadir"]
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-p", "--plateroot", dest="plateroot",
                      help ="(REQUIRED) Define the directory where the data plate info resides")
    parser.add_option("-f", "--familyfile", dest="familyfile",
                      help ="(REQUIRED) Define the directory for output files")
    parser.add_option("-x", "--metadir",
                      help="(Required) Meta directory holding CNV data")
    #OPTIONAL
    parser.add_option("-n", "--outputname", default="Output",
                      help="define the file name root for the output files")
    parser.add_option("-d", "--outputdir",
                      help ="define the directory for output files")
    parser.add_option("-t", "--threshold", default=.1,
                      help ="define a cutoff for confidence data")
    parser.add_option("-m", "--celmap", dest="celmap",
                      help="Cel Map file")
    parser.add_option("-c", "--chip", default=6,
                      help="Chip Type")
    parser.add_option("-b", "--build", default=18,
                      help="Human Genome Build")
    parser.add_option("-a", "--noallelemap", default=False,
                      action="store_true",
                      help="""Do not convert Probes to Alleles""")
    parser.add_option("-r", "--norscoding", default=False,
                      action="store_true",
                      help="""Do not convert SNP id to RS id""")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
        
    #VALIDATE PATHS
    lstOptionsToCheck = ['familyfile', 'plateroot', 'outputdir', 'metadir']
    if dctOptions.celmap:
        lstOptionsToCheck.append("celmap")
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    #METADIR
    if not dctOptions.noallelemap:
        pattern = re.compile("genomewidesnp_" + str(dctOptions.chip) + "_alleles[.]csv", re.IGNORECASE)
        allele_files = utils.findFiles(dctOptions.metadir, pattern)
        if len(allele_files)>0:
            dctAlleleMap = utils.readAllelesFile(allele_files[0])
        else:
            print "****No Allele Map Found**** "
            sys.exit(1)
    else:
        dctAlleleMap = {}
    
    #RECODE SNPIDs to RSIDs
    if not dctOptions.norscoding:
        print "\tLooking SNP map: genomewidesnp_" + str(dctOptions.chip) + ".rs_snp_map"
        pattern = re.compile("genomewidesnp_" + str(dctOptions.chip) + "[.]rs_snp_map", re.IGNORECASE)
        map_files = utils.findFiles(dctOptions.metadir, pattern)
        if len(map_files > 0):
            dctMapFile = utils.readSnpMapFile(map_files[0])
        else:
            print "\t*** Could not find SNP map, disabling SNP to RS conversion ***"
            dctMapFile = {}
            setattr(dctOptions, 'norscoding', True)
    else:
        dctMapFile = {}

    #COPY MAP FILE FOR FAWKES OUTPUT
    pattern = re.compile("genomewidesnp_" + str(dctOptions.chip) + "[.]hg" + str(dctOptions.build) + "[.]map", re.IGNORECASE)
    map_files = utils.findFiles(dctOptions.metadir, pattern)
    map_copy = os.path.join(dctOptions.outputdir, dctOptions.outputname + ".fawkes.map")
    shutil.copy(map_files[0], map_copy)  #Copy Map file for Later Analysis Use
            
    #LOAD CEL MAP
    if dctOptions.celmap:
        dctCelMap = utils.readCelMapFile(dctOptions.celmap)
    else:
        dctCelMap = {}
        
    #LOAD FAMILY FILE
    fam_copy = os.path.join(dctOptions.outputdir, dctOptions.outputname + ".fawkes.fam")
    shutil.copy(dctOptions.familyfile, fam_copy)  #Copy Fam file for Later Analysis Use
    dctFamMap = utils.readFamFile(dctOptions.familyfile)
    
    #CHECK PLATE PATHS
    pattern = re.compile('[.]merged[.]fawkes[.]calls', re.IGNORECASE)
    CallsPaths = utils.findFiles(dctOptions.plateroot, pattern)
    pattern = re.compile('[.]merged[.]fawkes[.]confs', re.IGNORECASE)
    ConfsPaths = utils.findFiles(dctOptions.plateroot, pattern)
    if not len(CallsPaths) == len(ConfsPaths):
        print "You are missing one or more files in your plate paths, please check file integrity"
        sys.exit(1)
        
    if not len(CallsPaths) > 0:
        print "Unable to find any files"
        
    #MAKE GVAR FILE
    ProcessData(CallsPaths, ConfsPaths, dctOptions, dctCelMap, dctFamMap, dctAlleleMap, dctMapFile)
    print "Finished -- Fawkes_To_Gvar.Py\n"
    
def ProcessData(CallsPaths, ConfsPaths, dctOptions, dctCelMap, dctFamMap, dctAlleleMap, dctMapFile):
    fOut = open(os.path.join(dctOptions.outputdir, dctOptions.outputname + ".fawkes.gvar"), "w")
    fOut.write("FID\tIID\tNAME\tAL1\tDOS1\tAL2\tDOS2\n")
    
    dctFamMissing = {}
    dropped_count = 0
    gathered_count = 0
    indiv_count = 0
    
    for file_number in range(len(CallsPaths)):
        
        CallsFile = open(CallsPaths[file_number])
        ConfsFile = open(ConfsPaths[file_number])
        calls_line = CallsFile.readline()
        confs_line = ConfsFile.readline()
            
        CelList = []
        #CHECK HEADER
        calls_fields = calls_line.split()
        confs_fields = confs_line.split()
        
        for items in range(len(calls_fields)):
            if calls_fields[items] == confs_fields[items]:
                CelList.append(calls_fields[items])
                continue
            else:
                print "Headers are not the same"
                sys.exit(1)
        
        if dctOptions.celmap:
            CelList = RemoveCels(CelList, dctOptions, dctCelMap)
        
        #GO THROUGH FILES
        for calls_line in CallsFile:
                
            confs_line = ConfsFile.readline()
            calls_fields = calls_line.split()
            confs_fields = confs_line.split()
            total_indiv = 0.0
            skipped_indiv = 0.0
            
            #CHECK IF THE CNPs ARE THE SAME
            snp_check = False
            if not snp_check:
                if calls_fields[0] == confs_fields[0]:
                    snp_check = True
                    snp_id = calls_fields[0]
                else:
                    print "CNVs are not in the proper order, please verify your Birdsuite output and try again"
                    sys.exit(1)
                    
            #SET PROBE VALUES
            if dctOptions.noallelemap:
                probeA = 'A'
                probeB = 'B'
            else:
                if dctAlleleMap.has_key(snp_id):
                    probeA = dctAlleleMap[snp_id][0]
                    probeB = dctAlleleMap[snp_id][1]
                else:
                    print "Allele map is missing important data for " + snp_id
                    print "Please fix this and restart the pipeline"
                    sys.exit(1)
                    
            #SET RS ID
            if not dctOptions.norscoding:
                if dctMapFile.has_key(snp_id):
                    snp_id = dctMapFile[snp_id]
                else:
                    print "SNP to RS Map is missing data for " + snp_id
                    print "Please fix this and restart the pipeline"
                    sys.exit(1)
                
            #WRITE FILE        
            for index in range(1,len(calls_fields)):
                total_indiv += 1
                if dctFamMap.has_key(CelList[index]):
                    cel_id = CelList[index]
                    strCall = calls_fields[index]
                    conf = confs_fields[index]
                    if strCall is None:
                        iA = -1
                        iB = -1
                    else: (iA, iB) = [int(strVal) for strVal in strCall.split(",")]
                    if iA == -1:
                        if iB != -1:
                            print "Strange call (" + strCall + ") for SNP " + snp_id
                            sys.exit(2)
                    if iA+iB != 2:
                        if float(conf) < float(dctOptions.threshold):
                            gathered_count += 1
                            #FIND OUT THE STATES THAT DATA IS REPRESENTED HERE
                            if conf == "NA" or float(conf) == -9:
                                fOut.write(("%s\t%s\t%s\t0\t1\t0\t1\n") % (dctFamMap[cel_id][0], cel_id, snp_id))
                            else:
                                fOut.write(("%s\t%s\t%s\t%s\t%s\t%s\t%s\n") % (dctFamMap[cel_id][0], cel_id, snp_id, probeA, iA, probeB, iB))
                        else:
                            dropped_count += 1
                    else:
                        continue
                else:
                    if not dctFamMissing.has_key(CelList[index]):
                        dctFamMissing[CelList[index]] = True
#                    skipped_indiv += 1
#                    if skipped_indiv > 5 and total_indiv > 20:    
#                        if ((skipped_indiv / total_indiv) > 0.8):
#                            print "Most of the individuals are not present in pedigree file (> 80%), You will likely need to provide a celMap"
#                            sys.exit(1)
                    continue
        indiv_count += len(CelList)
                        
    if dropped_count > 0:
        print ("\t(%s) of (%s)\tEvents Failed thresholding") % (dropped_count, gathered_count)
    if len(dctFamMissing.keys()) > 0:
        print ("\t(%s) of (%s)\tIndividuals not in the Family Data") % (len(dctFamMissing.keys()), indiv_count)
        for indiv in dctFamMissing.keys():
            print "\t" + indiv
    fOut.close()
    
def RemoveCels(list, dctOptions, dctCelMap):
    
    for index in range(len(list)):
        item = list[index] 
        item = utils.stripCelExt(item)
        
        if dctOptions.celmap and not item == 'cnp_id':
            if dctCelMap.has_key(item):
                item = dctCelMap[item]
        list[index] = item
    return list

if __name__ == "__main__":
    main()
    
