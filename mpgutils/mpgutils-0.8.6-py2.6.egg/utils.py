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


"""LOTS OF CONSTANTS, MMMM KAY?"""

import os
import fileinput
import glob
import numpy
import subprocess
import sys
import time
import re

#DEFAULTS
LIB_DIR="LIB_DIR"
CHIP_TYPE="CHIP_TYPE"
SMF_DEFAULT_INDEX="SMF_DEFAULT_INDEX"
SMF_OBSERVABLES="SMF_OBSERVABLES"
QNORM_PROBE_FILE="QNORM_PROBE_FILE"
UNIVERSAL_INTENSITY="UNIVERSAL_INTENSITY"
UNIVERSAL_QUANTILES="UNIVERSAL_QUANTILES"
EXEC_DIR="EXEC_DIR"

#Versions
V5="V5"
V6="V6"

iNUM_CHROMOSOMES=24

dctV5Defaults= {
                LIB_DIR:"/humgen/affy_info/GAPProduction/",
                CHIP_TYPE:"BI_SNP",
                SMF_DEFAULT_INDEX:"0-50",
                SMF_OBSERVABLES:"/humgen/cnp04/sandbox/normalization/SeqFragMix/observables/observables_500b_v2.binary",
                QNORM_PROBE_FILE:"/humgen/cnp04/sandbox/normalization/quantile/autosomal_probes.txt",
                UNIVERSAL_INTENSITY:"/humgen/cnp04/sandbox/data/universal_median-intensities.txt",
                UNIVERSAL_QUANTILES:"/humgen/cnp04/sandbox/data/universal_quantiles.txt",
                EXEC_DIR:"/fg/software/Affymetrix/1chip/"
                }

dctV6Defaults = {
                 EXEC_DIR:"/fg/software/Affymetrix/1chip/",
                 LIB_DIR:"/humgen/affy_info/GAPProduction/",
                 CHIP_TYPE:"GenomeWideEx_6"
                 }

dctDefaults = {V5:dctV5Defaults, V6:dctV6Defaults}


def getSupportedVersions ():
    return dctDefaults.keys()

def getDefault (version, name):
    """Returns the default for the variable name and the version.  If the version does not exist, or the variable does not exist, return None"""
    try:
        dctChip = dctDefaults[version]
        try:
            return dctChip[name]
        except KeyError:
            return None
    except KeyError:
        print >> sys.stderr, "Version " + version + " is not registered"
        return None
    
# This is supposed to be in subprocess, but it isn't there
def check_call(lstArgs, bVerbose=False):
    if bVerbose:
        print >> sys.stderr, time.asctime(), "Calling", " ".join(lstArgs)
    retcode = subprocess.call(lstArgs)
    if bVerbose:
        print >> sys.stderr, time.asctime(), "Done", lstArgs[0]
    if retcode != 0:
        raise Exception("ERROR: exit status %d from command %s" % (retcode, " ".join(lstArgs)))

def callWithLog(args, bVerbose=False, stdOutFileName=None, stdErrFileName=None):
    outFile = None
    errFile = None
    if stdOutFileName is not None:
        outFile=open(stdOutFileName, 'w')
    if stdErrFileName is not None:
        errFile=open(stdErrFileName, 'w')
             
    p = subprocess.Popen(args,
                         stdout=outFile,
                         stderr=errFile)
    p.wait()
    if outFile is not None:
        outFile.close()
    if errFile is not None:
        errFile.close()
        
def validateRequiredOptions(dctOptions, lstRequiredOptions):
    """Return true if the required arguments are valid, and false if at least one is not"""
    for strOpt in lstRequiredOptions:
        if getattr(dctOptions, strOpt) is None:
            print >> sys.stderr, 'ERROR:', strOpt, 'argument is required.'
            return False
    return True
        
def getCelFiles(strDirectory):
    d=strDirectory.rstrip("/")
    temp=d+"/*.[cC][eE][lL]";
    result = glob.glob(temp)
    result.sort()
    return result    

    
def raiseExceptionWithFileInput(fileInput, strFileType, strMessage):
    raise Exception("Error reading " + strFileType + " '" + fileInput.filename() + "' at line " +
                        str(fileInput.lineno()) + ": " + strMessage + ".")


def convertChromosomeStr(strChr):
    # Handle PAR like chrX
    if strChr == 'X' or strChr == 'PAR' or strChr=='XY':
        return '23'
    if strChr == 'Y':
        return '24'
    return strChr

dctComplements = {
    'A': 'T',
    'T': 'A',
    'G': 'C',
    'C': 'G',
    'N': 'N',
    'a': 't',
    't': 'a',
    'g': 'c',
    'c': 'g',
    'n': 'n',
    }

def complementBase(strBase):
    return dctComplements[strBase]

def repmat(mat, rowMultiplier, colMultiplier):
    if hasattr(numpy, "repmat"):
        return numpy.repmat(mat, rowMultiplier, colMultiplier)
    else: return numpy.tile(mat, (rowMultiplier, colMultiplier))



def parseAnnotationFile(strFile, bYieldHeaderLine=False):
    '''Create iterator that returns fields of annotation file split on "," '''
    fIn = open(strFile)

    # Skip header
    for strLine in fIn:
        if not strLine.startswith("#"):
            break

    if bYieldHeaderLine:
        strLine = strLine.rstrip("\n")
        assert strLine[0] == '"'
        assert strLine[-1] == '"'
        strLine = strLine[1:-1]
        yield strLine.split('","')
        

    for strLine in fIn:
        strLine = strLine.rstrip("\n")
        assert strLine[0] == '"'
        assert strLine[-1] == '"'
        strLine = strLine[1:-1]
        yield strLine.split('","')

    fIn.close()
    
def skipHeader(fIn, strStartsWith):
    while True:
        strLine = fIn.readline()
        if strLine.startswith(strStartsWith):
            return strLine
        if strLine == "":
            return None

def skipLeadingComments(fIn):
    while True:
        strHeader = fIn.readline()
        if not strHeader.startswith("#"):
            break
    return strHeader

def loadGenders(strPath):
    fIn = fileinput.FileInput([strPath])
    strHeader = fIn.readline().rstrip()
    lstRet = []
    if strHeader != "gender":
        raiseExceptionWithFileInput(fIn, "gender file", "Header line 'gender' not found")
    for strLine in fIn:
        strLine = strLine.rstrip()
        if not strLine.isdigit():
            raiseExceptionWithFileInput(fIn, "gender file", "Non-numeric gender")
        iGender = int(strLine)
        if iGender < 0 or iGender > 2:
            raiseExceptionWithFileInput(fIn, "gender file", "Gender must be 0 (female), 1 (male), or 2 (unknown)")
        # Treat unknowns like females
        if iGender == 2: iGender = 0
        lstRet.append(iGender)

    fIn.close()
    return lstRet

lstGENDERS = ["female", "male", "unknown"]

def genderToString(iGender):
    return lstGENDERS[iGender]

def loadSpecialProbes(dctRet, strPath):
    """For each special probe, add to dctRet
    dctRet[strProbeName] = tup(iFemaleCopies, iMaleCopies].
    These are added to dctRet so this method can be called to load multiple special probes files.
    if dctRet is None, a new dictionary is created."""
    if dctRet is None:
        dctRet = {}
    fIn = fileinput.FileInput([strPath])
    strHeader = skipLeadingComments(fIn)
    lstColumnHeaders = strHeader.split()
    if lstColumnHeaders != ["probeset_id", "chr", "copy_male","copy_female"]:
        raiseExceptionWithFileInput(fIn, "special probes file", "Strange header line")
    for strLine in fIn:
        lstFields = strLine.split()
        if lstFields[0] in dctRet:
            raiseExceptionWithFileInput(fIn, "special probes file", "Probe previously defined")
        if not lstFields[2].isdigit() or not lstFields[3].isdigit():
            raiseExceptionWithFileInput(fIn, "special probes file", "Non-numeric copy count")
        dctRet[lstFields[0]] = (int(lstFields[3]), int(lstFields[2]))

    fIn.close()
    return dctRet

def ensurePath(path):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        return path
    else:
        path, file = os.path.split(path)
        pattern = re.compile(str(file).replace(".", "[.]"), re.IGNORECASE)
        if os.path.exists(path):
            for item in os.listdir(path):
                match = pattern.search(item)
                if match:
                    return os.path.join(path, file)
            file = os.path.join(path,file)
            print "Creating file: " + file
            open(file, "w").close()
            return file
        else:
            return None
    return path

def mergeFiles (lstFiles, outFile):
    lstFileHandles=[open(f, 'r') for f in lstFiles]
    startHandle=lstFileHandles[1]
    fOut = open (outFile, "w")
    
    successFlag=True
    while startHandle:
        
        lines=[f.readline() for f in lstFileHandles]
        data=lines[0].split()
        
        if len(data)==0: break;  #hit the end of the data.
        
        id=data[0]   
        otherLines=lines[1:]
        otherLines=[l.split() for l in otherLines]
        
        otherIDs=[l[0] for l in otherLines]
        for o in otherIDs:
            if o!=id: 
                print ("Line of first file and subsequent file don't match:" + "original[" + id + "] new [" + o +"]")
                successFlag=False
            
        otherLines=[l[1:] for l in otherLines]
        
        for l in otherLines: data.extend(l)
        data.append("\n")
        finalLine = "\t".join(data)
        fOut.write(finalLine)
        
    fOut.close()    
    return (successFlag)

def validatePath(path):
    if (os.path.exists(os.path.expanduser(path))):
        return os.path.expanduser(path)
    else:
        return None

def validatePathArgs (dctOptions, lstOptionsToCheck, quitOnFail):
    """Validate the options that point to files."""
    for strOpt in lstOptionsToCheck:
        path = getattr(dctOptions, strOpt)
        newPath = validatePath(path)
        if newPath:
            setattr(dctOptions, strOpt, newPath)
        else:
            print >> sys.stderr, 'ERROR: Could not find "' +strOpt+ '" @ ' +path
            setattr(dctOptions, strOpt, None)
            if quitOnFail:
                sys.exit(1)
    return dctOptions

def readFamFile (family_file):
    #PLINK FAMILY FILE
    fIn = open(family_file)
    dctFamMap = {}
    
    for strLine in fIn:
        if(strLine[0]== '#'):
            continue
        
        Fields = strLine.split()
        IID=Fields[1]
        FID=Fields[0]
        MID=Fields[2]
        PID=Fields[3]
        GEND=Fields[4]
        PHEN=Fields[5]
        dctFamMap[IID] = [FID,MID,PID,GEND,PHEN]
    
    return dctFamMap

def checkFamFile (family_file, usr_proportion):
    #PLINK FAMILY FILE
    #CHECK FOR PROPORTION OF 0 or -9 (missing) Phenotypes
    #MISSING MUST NOT EXCEED usr_proportion
    fIn = open(family_file)
    lines = 0.0
    missing = 0.0
    
    for strLine in fIn:
        Fields = strLine.split()
        if Fields[5] == '0' or Fields[5] == '-9':
            missing += 1.0
        lines += 1.0
        
    proportion = missing/lines
    if proportion > usr_proportion:
        return False
    return True

def readCelMapFile (cel_map_file):
    fIn = open(cel_map_file)
    dctCelMap = {}
        
    for strLine in fIn:
        if(strLine[0]== '#'):
            continue
        
        Fields = strLine.split()   
        celID = Fields[0]
        celID = stripCelExt(celID)
        IID = Fields[1]
        dctCelMap[celID] = IID
        
    return dctCelMap

def readSnpMapFile(map_file):
    fIn = open(map_file)
    dctMapFile = {}
    
    for strLine in fIn:
        Fields = strLine.split()
        rsID = Fields[0]
        snpID = Fields[1]
        dctMapFile[snpID] = rsID
    
    return dctMapFile
        
def stripCelExt(item):
    p = re.compile( '[.]cel', re.IGNORECASE )
    m = p.search(item)
    if m:
        item = item[:-4]
    return item

def readAllelesFile (alleles_file):
    #GENOME WIDE SNP TO ALLELES FILE
    fIn = open(alleles_file)
    dctAllelesMap = {}
    
    for strLine in fIn:
        fields = strLine.split()
        SNP=fields[0]
        aProbe = fields[1]
        bProbe = fields[2]
        dctAllelesMap[SNP] = [aProbe, bProbe]
    return dctAllelesMap

def findFiles(folder_root, pattern):
    Files = []
    for root, dirs, files in os.walk(folder_root, False):
        for name in files:
            match = pattern.search(name)
            if match:
                Files.append(os.path.join(root, name))
    Files.sort()
    return Files
            
def iterateWhitespaceDelimitedFile(strPath, iNumFieldsExpected=None, bSkipComments=False, bSkipHeader=False):
    fIn = fileinput.FileInput([strPath])
    if bSkipComments:
        strFirstLine = skipLeadingComments(fIn)
    else:
        strFirstLine = None
    if bSkipHeader:
        if strFirstLine is None:
            fIn.readline()
        else:
            strFirstLine = None

    if strFirstLine is not None:
        lstFields = strFirstLine.split()
        if iNumFieldsExpected is not None and len(lstFields) != iNumFieldsExpected:
            raise Exception("Incorrect number of fields in file " + strPath + "; Line: " + str(fIn.lineno()))
        yield lstFields

    for strLine in fIn:
        lstFields = strLine.split()
        if iNumFieldsExpected is not None and len(lstFields) != iNumFieldsExpected:
            raise Exception("Incorrect number of fields in file " + strPath + "; Line: " + str(fIn.lineno()))
        yield lstFields

    fIn.close()

iTFAM_FAMILY_ID_INDEX=0
iTFAM_INDIVIDUAL_ID_INDEX=1
iTFAM_PATERNAL_ID_INDEX=2
iTFAM_MATERNAL_ID_INDEX=3
iTFAM_GENDER_INDEX=4

        
def load_tfam(strTfamPath, lstIndicesToLoad=None):
    """Returns a list of tuples (strFamilyID, strIndividualID, strPaternalID, strMaternalID, iGender,
    iPaternalIndex, iMaternalIndex).  iPaternalIndex and iMaternalIndex, if not None, are indices
    into this list.  iGender is 1=male, 2=female, None=unknown"""
    fIn = open(strTfamPath)
    lstRet = []
    # Maps (strFamilyID, strIndividualID) to index of individual in lstRet
    dctIndividualMap = {}
    for iIndex, strLine in enumerate(fIn):
        if lstIndicesToLoad is not None and iIndex not in lstIndicesToLoad:
            continue
        lstFields = strLine.split()
        if len(lstFields) < iTFAM_GENDER_INDEX + 1:
            raise Exception("Not enough fields on TFAM line: " + strLine)
        tupIndividual = (lstFields[iTFAM_FAMILY_ID_INDEX], lstFields[iTFAM_INDIVIDUAL_ID_INDEX])
        if tupIndividual in dctIndividualMap:
            print >> sys.stderr, "WARNING: Individual defined more than once on TFAM line:", strLine.rstrip()
        else:
            dctIndividualMap[tupIndividual] = len(lstRet)

        lstFields[iTFAM_GENDER_INDEX] = convertTFAMGender(lstFields[iTFAM_GENDER_INDEX])
        lstFields[iTFAM_PATERNAL_ID_INDEX] = convertTFAMParentID(lstFields[iTFAM_PATERNAL_ID_INDEX])
        lstFields[iTFAM_MATERNAL_ID_INDEX] = convertTFAMParentID(lstFields[iTFAM_MATERNAL_ID_INDEX])

        # Discard phenotype column and anything else after that
        del lstFields[iTFAM_GENDER_INDEX+1:]
        lstRet.append(lstFields)

    for tupIndividual in lstRet:
        iPaternalIndex = None
        if tupIndividual[iTFAM_PATERNAL_ID_INDEX] is not None:
            iPaternalIndex = dctIndividualMap.get((tupIndividual[iTFAM_FAMILY_ID_INDEX],
                                                   tupIndividual[iTFAM_PATERNAL_ID_INDEX]),
                                                  None)
        iMaternalIndex = None
        if tupIndividual[iTFAM_MATERNAL_ID_INDEX] is not None:
            iMaternalIndex = dctIndividualMap.get((tupIndividual[iTFAM_FAMILY_ID_INDEX],
                                                   tupIndividual[iTFAM_MATERNAL_ID_INDEX]),
                                                  None)
        tupIndividual += [iPaternalIndex, iMaternalIndex]

    fIn.close()
    return lstRet

def convertTFAMGender(strGender):
    "Returns 0 for female, 1 for male, None for unknown"
    if strGender in ("1", "2"):
        return 2 - int(strGender)
    return None

def convertTFAMParentID(strID):
    if strID == "0":
        return None
    return strID

def assertRaises(excClass, callableObj, *args, **kwargs):
    """Fail unless an exception of class excClass is thrown
       by callableObj when invoked with arguments args and keyword
       arguments kwargs. If a different type of exception is
       thrown, it will not be caught, and the test case will be
       deemed to have suffered an error, exactly as for an
       unexpected exception.
       Stolen from unittest.py
    """
    try:
        callableObj(*args, **kwargs)
    except excClass:
        return
    else:
        if hasattr(excClass,'__name__'): excName = excClass.__name__
        else: excName = str(excClass)
        raise AssertionError, "%s not raised" % excName

def iterateProbeLocus(strProbeLocusPath):
    """Read probe locus file, converting chromosome names to numbers, converting PAR to X, and skipping MT"""
    for lstFields in iterateWhitespaceDelimitedFile(strProbeLocusPath, iNumFieldsExpected=3):
        if lstFields[1] == "MT":
            continue
        yield [lstFields[0], convertChromosomeStr(lstFields[1]), int(lstFields[2])]
        
def loadProbeLocus(strProbeLocusPath):
    dctRet = {}
    for lstFields in iterateProbeLocus(strProbeLocusPath):
        # Don't load SNPs with no locus
        if lstFields[1] != '0':
            dctRet[lstFields[0]] = (lstFields[1], lstFields[2])
    return dctRet
