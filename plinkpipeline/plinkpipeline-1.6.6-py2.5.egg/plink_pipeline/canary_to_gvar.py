#!/usr/bin/env python
import optparse
from mpgutils import utils
import sys
import os
import re
import shutil

#GLOBALS
dctIndivToFamMap = {}
dctCelFileMap = {}
dctIndivMap = {}
dctCallFile = {}
    
def main(argv = None):
    if argv is None:
        argv = sys.argv

    lstRequiredOptions=["familyfile", "plateroot"]
    parser = optparse.OptionParser(usage=__doc__)
    
    #OPTION PARSING!
    global output_root, output_name

    #REQUIRED
    parser.add_option("-f", "--familyfile",
                      help ="(Required) Define the directory for output files")
    parser.add_option("-p", "--plateroot",
                      help ="(Required) Define the directory where the data plate info resides")
    #OPTIONAL
    parser.add_option("-o", "--outputdir",
                      help ="Define the directory for output files")
    parser.add_option("-n", "--outputname", default="Output",
                      help="define the file name root for the output files")
    parser.add_option("-t", "--threshold", default=.1,
                      help ="define a cutoff for confidence data")
    parser.add_option("-m", "--celmap", dest="celmap",
                      help="Cel Map file")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
        
    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
    #VALIDATE PATHS
    lstOptionsToCheck = ['familyfile', 'plateroot', 'outputdir']
    if dctOptions.celmap:
        lstOptionsToCheck.append("celmap")
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    
    #CHECK PLATE PATHS
    plate_root = utils.validatePath(dctOptions.plateroot)
    pattern = re.compile('[.]merged[.]canary[.]calls', re.IGNORECASE)
    CallsPaths = utils.findFiles(plate_root, pattern)
    pattern = re.compile('[.]merged[.]canary[.]confs', re.IGNORECASE)
    ConfsPaths = utils.findFiles(plate_root, pattern)
    
    
    #VERIFY FILES ARE THE SAME
    if not len(CallsPaths) == len(ConfsPaths):
        print "You are missing one or more files in your plate paths, please check file integrity"
        sys.exit(1)
    
    #FAMILY FILE
    fam_copy = os.path.join(dctOptions.outputdir, dctOptions.outputname + ".canary.fam")
    shutil.copy(dctOptions.familyfile, fam_copy)  #Copy Fam file for Later Analysis Use
    ReadFamFile(dctOptions.familyfile)
    
    #CEL MAP FILE 
    if dctOptions.celmap:
        ReadCelMapFile(dctOptions.celmap)
    
    #CALLS FILE
    for calls_path in CallsPaths:
        ReadCallsFile(calls_path, dctOptions)
        
    #CREATE OUTPUT
    fOut = open(os.path.join(dctOptions.outputdir, dctOptions.outputname + ".canary.gvar"), "w")
    fOut.write("FID\tIID\tNAME\tAL1\tDOS1\tAL2\tDOS2\n")
    ReadConfsFiles(ConfsPaths, dctOptions, fOut)
    
    print "Finished Canary_To_Gvar.Py\n"
    
def MakeMap(list, dctOptions):
    
    count = 0
    returnMap = {}
    for item in list:
        
        item = StripCelExt(item)
        
        if dctOptions.celmap and not item == 'cnp_id':
            if dctCelFileMap.has_key(item):
                item = dctCelFileMap[item]
                    
        returnMap[item] = count
        count += 1
    return returnMap

def StripCelExt(item):
    p = re.compile( '[.]cel', re.IGNORECASE )
    m = p.search(item)
    if m:
        item = item[:-4]
    return item

def ReadCelMapFile (cel_map_file):
    CelMapFile = open(cel_map_file)
    global dctCelFileMap
        
    for strLine in CelMapFile:
        if(strLine[0]== '#'):
            continue
        
        Fields=strLine.split()   
        CelID=Fields[0]
        
        #Make sure .CEL isn't appended to the name
        CelID = StripCelExt(CelID)
            
        IID=Fields[1]
        dctCelFileMap[CelID] = IID
    
def ReadFamFile (family_file):
    FamilyFile = open(family_file)
    global dctIndivToFamMap
    
    for strLine in FamilyFile:
        Fam_Value = []
        
        if(strLine[0]== '#'):
            continue
        
        Fields = strLine.split()
        IID=Fields[1]
        FID=Fields[0]
        dctIndivToFamMap[IID] = FID
        
def ReadCallsFile (calls_path, dctOptions):
    CallsFile = open(calls_path)
    global dctCallFile   
        
    header_complete = False
    for strLine in CallsFile:
        CallFileFields = strLine.split()
        
        #HEADER
        if not header_complete:
            dctCallFile = MakeMap(CallFileFields, dctOptions)
            for key in dctCallFile.keys():
                if not dctIndivMap.has_key(key):
                    dctCNVType = {}
                    dctIndivMap[key] = dctCNVType
            header_complete=True
            continue
        
        #BODY
        CNVID = CallFileFields[0]
        for key in dctCallFile.keys():
            
            #REVIEW AND TAKE OUT IF POSSIBLE
            if dctCallFile[key] == 0:
                continue
            
            Field = CallFileFields[dctCallFile[key]]
            tmpMap = dctIndivMap[key]
            if Field == "NA":
                tmpMap[CNVID] = int(-9)
            else:
                tmpMap[CNVID] = int(Field)
                
def ReadConfsFiles (ConfsPaths, dctOptions, gvarFile):
    dctFamMissing = {}
    dctCNVMissing = {}
    dropped_count = 0
    gathered_count = 0
    indiv_count = 0
        
    for confs_path in ConfsPaths:
        ConfsFile = open(confs_path)
        
        #MAKE GVAR FILE
        header_complete = False
        for strLine in ConfsFile:
            ConfFileFields = strLine.split()
    
            #HEADER
            if(header_complete == False):
                dctConfFile = MakeMap(ConfFileFields, dctOptions)
                header_complete=True
                continue
            
            CNVID = ConfFileFields[0]
            for key in dctConfFile.keys():
                if dctIndivMap.has_key(key):
                    if key == 'cnp_id':
                        continue
                    else:
                        tmpMap = dctIndivMap[key]
                        if tmpMap.has_key(CNVID) and dctIndivToFamMap.has_key(key):
                           
                            field = ConfFileFields[dctConfFile[key]]
                            if field == "NA":
                                gvarFile.write(("%s\t%s\t%s\t0\t1\t0\t1\n") % (dctIndivToFamMap[key],key,CNVID))
                            elif float(field) > float(dctOptions.threshold) or float(field) == -9 or tmpMap[CNVID] == -9:
                                if float(field) > float(dctOptions.threshold):
                                    dropped_count += 1
                                gvarFile.write(("%s\t%s\t%s\t0\t1\t0\t1\n") % (dctIndivToFamMap[key],key,CNVID))
                                
                            else:
                                gvarFile.write(("%s\t%s\t%s\tX\t0\tA\t%s\n") % (dctIndivToFamMap[key],key,CNVID,tmpMap[CNVID]))
                                gathered_count += 1
                        else:
                            if not tmpMap.has_key(CNVID):
                                if not dctCNVMissing.has_key(key):
                                    dctCNVMissing[key] = True
                                continue
                            elif not dctIndivToFamMap.has_key(key):
                                if not dctFamMissing.has_key(key):
                                    dctFamMissing[key] = True
                                continue
                else:
                    print "\t" + key + " is missing"
                    continue
        indiv_count += len(ConfFileFields)
                
    if not dctOptions.quiet and dropped_count > 0:
        print ("\t(%s) of (%s)\tFailed thresholding") % (dropped_count, gathered_count)
    if not dctOptions.quiet and len(dctFamMissing.keys()) > 0:
        print ("\t(%s) of (%s)\t\tIndividuals not in the Family Data") % (len(dctFamMissing.keys()), indiv_count)
        for indiv in dctFamMissing.keys():
            print "\t" + indiv
            
if __name__ == "__main__":
    main()
    
