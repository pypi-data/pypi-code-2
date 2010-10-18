#!/usr/bin/env python


# Written by Manuel A. Rivas
# Updated 08.11.2009

# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2009 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$

    
   
import GenerateCIFFile
import FinalAnnotation, CleanUpSNPCalls, EMFreqAssocStrandNew, CalphaRareTest, runsamtools, runsamtoolsparallel, SAMPileupAnalysis, SAMpileuphelper
import GenerateErrorModelrpy2
import PlotVisualizations
import IndividualPoolSummary
#import SyzygyPowerNew
import Learn2ndbestIntensity
#import CleanUpFiles
#import GenerateErrorModel
import AnnotateSNP
from mpgutils import utils    
from mpgutils.RUtils import RscriptToPython
import runrscript 
#import runrscriptparallel
import runrscriptparallel2
import SyzygyPower
from optparse import OptionParser;                                                                                                                                                                                                      
import sys,re
import numpy
#import runparsescript
import ParseAnnotation
import GenerateSNPCallsFile, GenerateAllCallsFile
from string import *
import pp
from pp import *
import EMFreqAssocStrandFixed


def main(argv = None):
    if not argv:
        argv = sys.argv
    lstRequiredOptions = ["tgf", "pif","rarethr","samtoolspath","hg","sndb"]
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)
    #REQUIRED Commands
    parser.add_option("-t","--tgf", 
                      help="Experimental Target File")
    parser.add_option("-i","--pif", 
                      help="Pool/Sample Info File")
    parser.add_option("-r","--rarethr",
                      help="Frequency Threshold for classifying variant as rare (default = .03)")
    parser.add_option('-g',"--hg",
    
                      help = "Specify Human Genome build being used (Currently 17 or 18)")
    
    parser.add_option('-s',"--samtoolspath",
                      help = "Specify SAMTools Path")
    parser.add_option('-n', "--sndb",
                      help = "2nd best base annotation with Quality Scores (true or false)",
                      default = "false")
    parser.add_option('-z',"--threaded",
                        help = "Allow Threading (default=false)",
                        default = "false")
    #OPTIONAL Commands
    parser.add_option('-u', "--ncpu",
                      help = "Number of CPUs",
                      default = 1)
    parser.add_option("-q", "--bqthr",
                      help="Base Quality Threshold (default Q = 22)",
                      default = 22)
    parser.add_option("-m", "--mqthr",
                      help="Mapping Quality Threshold (default Q = 1)",
                      default = 1)
    parser.add_option('-d', "--dbsnp",
                      help="dbSNP File")
    parser.add_option('-p', "--plots",
                      help="Generates Plots for Error Modeling, Frequency Estimation, Power Computations, and Calpha Diagnostics (true or false)")
    parser.add_option('-b', "--bds",
                      help="Bounds for Calpha Test (default = 5)",
                      default = 5)
    
    parser.add_option('-o',"--outputdir",
                      help="Define directory for output files")
    parser.add_option('-f',"--ref",
                      help = "FASTA for Reference Genome")
    parser.add_option('-c', "--cif",
                      help = " Coordinate File for SAMTools (default: generate from target file)",
                      default = "")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    #Validate Input Parameters
#===============================================================================
#    lstValidbuild = ['17','18']
#    if not (dctOptions.hg in lstValidbuild):
#        print "You entered a wrong build type"
#        sys.exit(1)
#    
#    #VALIDATE OUTPUT
#    if not dctOptions.outputdir:
#        setattr(dctOptions, 'outputdir', sys.path[0])
#    else:
#        pass
#    
#   
#    Syzygy Pooled Sequencing Pipeline
#   
#    
#    CREATE Position Map from Target File 
#    if not dctOptions.cif:
#        possible_args = ["tgf","outputdir","samtoolspath","pif"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n------Generating Position Files--------"
#        GenerateCIFFile.main(current_args)
#    
#    # Run Samtools 
#    if dctOptions.samtoolspath and dctOptions.ncpu == 1:
#        
#        if dctOptions.cif:
#            possible_args = ["cif","ref","pif","outputdir","samtoolspath","sndb"]
#            current_args = MakeArguments(possible_args,dctOptions)
#    #        print current_args
#            print "\n------Running SAMTools------------------"
#            runsamtools.main(current_args)
#            
#        else:
#            possible_args = ["tgf","ref","pif","outputdir","samtoolspath","sndb"]
#            current_args = MakeArguments(possible_args,dctOptions)
#     #       print current_args
#            print "\n------Running SAMTools------------------"
#            runsamtools.main(current_args)
#    elif dctOptions.samtoolspath and dctOptions.ncpu > 1:
#        
#        if dctOptions.cif:
#            possible_args = ["cif","ref","pif","outputdir","samtoolspath","sndb","ncpu"]
#            current_args = MakeArguments(possible_args,dctOptions)
#    #        print current_args
#            print "\n------Running SAMTools Parallel------------------"
#            runsamtoolsparallel.main(current_args)
#            
#        else:
#            possible_args = ["tgf","ref","pif","outputdir","samtoolspath","sndb","ncpu"]
#            current_args = MakeArguments(possible_args,dctOptions)
#     #       print current_args
#            print "\n------Running SAMTools Parallel------------------"
#            runsamtoolsparallel.main(current_args)
#        
#    else:
#        print "You must provide Sam Tools Path"
#        sys.exit(2)
#     #    Raise Exception Error ; EXIT
#    
#    # Run pileup_analysis 
#    if dctOptions.bqthr and dctOptions.mqthr and dctOptions.dbsnp and dctOptions.pif:
#        possible_args = ["bqthr","mqthr","dbsnp","pif"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n---------Running Pileup Analysis-------------------"     
#        SAMPileupAnalysis.main(current_args) 
#        
#    elif dctOptions.pif: 
#        possible_args = ["pif","outputdir"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n---------Running Pileup Analysis-------------------"
#        SAMPileupAnalysis.main(current_args)
# 
# 
# #     Run Error Modeling
#    if dctOptions.pif and dctOptions.outputdir:
#        possible_args = ["outputdir","pif","hg","dbsnp"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n---------Generating Error Model------------------"
#        GenerateErrorModelrpy2.main(current_args)
#        
#        
#    # Remove .coverage and .error.coverage files from directory 
#    if dctOptions.pif and dctOptions.outputdir and dctOptions.ncpu == 1:
#        possible_args = ["outputdir","pif"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n-------Computing LOD scores---------------------"
#        runrscript.main(current_args)
#        
#===============================================================================
# #===============================================================================
#        
#        # This should be threaded (sent in parallel to clusters). 
#    if dctOptions.ncpu > 1:
#        possible_args = ["outputdir","pif","ncpu"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n--------Running Parallel Execution of LOD Scores -----"
#        runrscriptparallel2.main(current_args)
# 
#===============================================================================
     
  #     Detect SNPs get Good List and Bad List
    if dctOptions.dbsnp and dctOptions.pif and dctOptions.hg:
        possible_args = ["outputdir","pif","dbsnp","hg"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n---------Cleaning Up SNP Calls---------------------------"
        CleanUpSNPCalls.main(current_args)
         
          
         
    #   Call SNPs (Check if LSF option is available) 
          
         
     #    print "\n-------Select Quality of SNPs-----------------"
    
#===============================================================================
#     # Annotation 
#    if dctOptions.outputdir:
#        possible_args = ["outputdir"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n------Annotating SNP Candidattes-------------------------"
#        AnnotateSNP.main(current_args)
#     
#     # Clean up Annotation File
#    if dctOptions.outputdir:
#        possible_args = []
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n------Cleaning up Annotation File-------------------------"
#        ParseAnnotation.main(current_args)
#         
#===============================================================================
#     Run EM for frequency/association testing and annotation
    if dctOptions.outputdir and dctOptions.pif:
        possible_args = ["outputdir","pif"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Frequency and Association Testing-------"
        EMFreqAssocStrandFixed.main(current_args)
    
    # With 2nd Best Base Annotation Run this to add columns 
    if dctOptions.outputdir and dctOptions.sndb == 'true':
        possible_args = ["outputdir","sndb"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Running Second Best Base Analysis------"
        Learn2ndbestIntensity.main(current_args)
        
        
    if dctOptions.outputdir:
        possible_args = ["outputdir"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Generating Final Annotations--------------------"
        FinalAnnotation.main(current_args)
        
    if dctOptions.outputdir:    
        possible_args = ["outputdir"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Generating .snpcalls File--------------------"
        GenerateSNPCallsFile.main(current_args)
    
    
    if dctOptions.outputdir and dctOptions.pif:
        possible_args = ["outputdir","pif"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Generating All Calls File--------------------"
        GenerateAllCallsFile.main(current_args)
    
    if dctOptions.outputdir:
        possible_args = ["outputdir"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Creating Pool By Pool Summary ---------------"
        IndividualPoolSummary.main(current_args) 
   
    #Run Calpha Test    
    if dctOptions.outputdir and dctOptions.pif and dctOptions.tgf:
        possible_args = ["outputdir","pif","tgf"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n-------Rare Variant Testing--------------------"
        CalphaRareTest.main(current_args)       
        
    # Run Power File  
#===============================================================================
#    if dctOptions.outputdir and dctOptions.pif and dctOptions.tgf:
#        possible_args = ["outputdir","pif","tgf"]
#        current_args = MakeArguments(possible_args,dctOptions)
#        print "\n-------Evaluating Power to detect singletons--------------------"
#        SyzygyPower.main(current_args)       
#===============================================================================
    
 #===============================================================================
    if dctOptions.outputdir:
        possible_args = ["outputdir"]
        current_args = MakeArguments(possible_args,dctOptions)
        print "\n---------Plotting Power Visualizations---------------------------"
        PlotVisualizations.main(current_args)
        
    
#================================================================================
#  Move Leftover Files to Scratch Folder
#================================================================================            

    if dctOptions.outputdir and dctOptions.pif:
        piffile = open(dctOptions.pif,'r').readlines()
        scratchpath = os.path.join(dctOptions.outputdir,'scratch/')
        resultspath = os.path.join(dctOptions.outputdir,'results/')
        ensurePathSyzygy(scratchpath)
        ensurePathSyzygy(resultspath)
        
        for line in piffile[1:]:
            filemove = []
            line = line.rstrip()
            line = line.split()
            pool = line[0]
            filemove.append(str(pool) + '.pileup')
            filemove.append(str(pool) + '.pileup.' + str(dctOptions.bqthr) + 'thresholded.coverage')
            filemove.append(str(pool) + '.combined.error.coverage')
            filemove.append(str(pool) + '.combined.error.coverage.calls')
            filemove.append(str(pool) + '.pileup' + str(dctOptions.bqthr) + '.r.miscallrate.plots001.pdf')
            filemove.append(str(pool) + '.pileup' + '.bq' + str(dctOptions.bqthr) + '.mq' + str(dctOptions.mqthr) + '.bes')
            filemove.append(str(pool) + '.pileup' + str(dctOptions.bqthr) + '.r' + '.miscallrate.' + 'plots001.png')
            filemove.append(str(pool) + '.pileup' + str(dctOptions.bqthr) + '.r' + '.miscallrate.' + 'plots002.png')
            filemove.append(str(pool) + '.pileup' + str(dctOptions.bqthr) + '.r' + '.miscallrate.' + 'plots003.png')
            filemove.append('error.model.pooledexperiment001.png')
            filemove.append('error.model.pooledexperiment002.png')
            filemove.append('error.model.pooledexperiment003.png')
            filemove.append(str(dctOptions.tgf) + '.cif')
            
            for src in filemove:
                srcpath = os.path.join(dctOptions.outputdir,src)
                if os.path.exists(srcpath):
                    last_part = os.path.split(src)[1]
                    os.rename(srcpath,os.path.join(scratchpath,last_part))
        filemove = []
        filemove.append('miscallrate.universal.' + str(dctOptions.bqthr) + '001' + '.pdf')
        filemove.append('snps.annotation.full.1')
        filemove.append('snplist.alleles.nc')
        filemove.append('snplist.alleles.utr')
        filemove.append('snplist.alleles.utrncnt')
        filemove.append('snplist.alleles.ns')
        filemove.append('snplist.alleles.syn')
        filemove.append('snplist.alleles.high')
        filemove.append('snplist.alleles.poor')
        filemove.append('snplist.alleles.readyannot')
        filemove.append('EMFreqAssoc.out')
        for src in filemove:
            srcpath = os.path.join(dctOptions.outputdir,src)
            if os.path.exists(srcpath):
                last_part = os.path.split(srcpath)[1]
                os.rename(srcpath,os.path.join(scratchpath,last_part))
            
        filemove = []
        filemove.append('snps.dosage.pool')
        filemove.append('snps.dosage')
        filemove.append('PooledExperiment.summary')
        filemove.append('PooledExperiment.pbp')
        filemove.append('PooledExperiment.allpositions')
        filemove.append('PooledExperiment.snpcalls')
        filemove.append('PooledExperiment.pf')
        filemove.append('heatmap.exon.matrix')
        filemove.append('RareTest.Calpha.regions')
        filemove.append('RareTest.Calpha')
        filemove.append('RareTest.Calpha.mix')
        filemove.append('Power001.eps')
        filemove.append('Power001.pdf')
        for src in filemove: 
            pathrewrite = os.path.join(dctOptions.outputdir,src)
            if os.path.exists(pathrewrite):
                srcpath = pathrewrite
                last_part = os.path.split(srcpath)[1]  
                os.rename(srcpath,os.path.join(resultspath,last_part))
                
                
def ensurePathSyzygy(path):
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
        else:
            os.mkdir(path)
            print "Creating Directory: " + path
            
            
            
def MakeArguments(possible_args,dctOptions):
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