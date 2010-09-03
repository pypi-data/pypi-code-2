'''
Created on Aug 27, 2009

@author: nemesh
'''

import optparse
import sys
import mpgutils.utils as utils
import os

import birdsuite.cn_annotate_allele_summary
import birdsuite.cn_locus_summarize
import birdsuite.cn_probeset_summarize
import birdsuitepriors.canary.prep_clusters
from mpgutils import mergeMatrixes
from mpgutils.RUtils import RscriptToPython

class EnvironmentSpec(object):
    def __init__(self, intensityFile, genotypeFile, probe_locus, tempDir, basename, outputFile, force_cn_summarization, 
                 cnpDefsFile, missingValueLabel, normalizationProbes, mapFile, offSetFile, minNumSamples, 
                 popFile, famFile, mapFileOut, bVerbose):
        
        self._intensityFile = intensityFile
        self._genotypeFile = genotypeFile
        self._tempDir = tempDir
        self._outputFile = outputFile
        self._probe_locus= probe_locus
        self._basename = basename
        self._force_cn_summarization = force_cn_summarization
        self._cnpDefsFile = cnpDefsFile
        self._missingValueLabel = missingValueLabel
        self._normalizationProbes= normalizationProbes
        self._mapFile = mapFile
        self._offSetFile = offSetFile
        self._minNumSamples = minNumSamples
        self._popFile = popFile
        self._famFile = famFile
        self._mapFileOut = mapFileOut
        self._bVerbose = bVerbose
        
    def probe_locus(self):
        return self._probe_locus
    
    def missingValueLabel(self):
        return self._missingValueLabel
    
    def cnpDefsFile(self):
        return self._cnpDefsFile
    
    def intensityFile(self):
        return self._intensityFile

    def genotypeFile(self):
        return self._genotypeFile
            
    def tempDir(self):
        return self._tempDir
    
    def outputFile(self):
        return self._outputFile
    
    def basename(self):
        return self._basename
    
    def normalizationProbes(self):
        return self._normalizationProbes
    
    def mapFile(self):
        return self._mapFile
    
    def offSetFile(self):
        return self._offSetFile
    
    def minNumSamples(self):
        return self._minNumSamples
    
    def popFile(self):
        return self._popFile
    
    def famFile(self):
        return self._famFile
    
    def mapFileOut(self):
        return self._mapFileOut
    
    def sumZFile(self):
        if self._tempDir is not None :
            return (self._tempDir+"/birdseed.sumz")

    def force_cn_summarization(self):
        return self._force_cn_summarization
    
    def annotateAlleleSummaryOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".annotated_summary"
        return (outFile)
    
    def locusSummarizeOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".locus_summary"
        return (outFile)
    
    def cnSummarizeOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".probeset_summary"
        return (outFile)
    
    def prepClusterOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".prepped_clusters"
        return (outFile)
    
    def genotypesAligned(self):
        genotypesOut=self._tempDir+"/" + self._basename+ ".genotypes.aligned"
        return (genotypesOut)
    
    def intensitiesAligned(self):
        intensity=self.cnSummarizeOut()+".aligned"
        return (intensity)
    
    def genotypesAlignedQCed(self):
        return (self.genotypesAligned()+".fld_qc")
    
    def intensitiesAlignedQCed(self):
        return (self.intensitiesAligned()+".fld_qc")
    
    def canaryTestDir(self):
        r=self._tempDir+"/per_plate_data"
        return (r)
    
    def filteredCNVDefsFile(self):
        outFile=self._tempDir+"/"+ self._basename+ ".cnv_defs.first_qc"
        return (outFile)
    
    def priorsFileWithoutQC(self):
        return (self._tempDir+"/" + self._basename+".canary_priors.no_qc")
        
        
def annotate_allele_summary(envSpec):
    argv=["cn_annotate_allele_summary",
          "--probe_locus", envSpec.probe_locus(),
          "--summary",envSpec.intensityFile(),
          "--output", envSpec.annotateAlleleSummaryOut(),
          "--tmpdir", envSpec.tempDir()]
    
    birdsuite.cn_annotate_allele_summary.main(argv)
    print ("FINISHED annotate allele summary")
    
def locus_summarize(envSpec):
    argv=["cn_locus_summarize", 
          "--output", envSpec.locusSummarizeOut(),
          "--missing_value_label", envSpec.missingValueLabel()]
    if envSpec.force_cn_summarization():
          t=["--force_cn_summarization"]
          argv.extend(t)
          
    argv.extend([envSpec.annotateAlleleSummaryOut()])
    
    birdsuite.cn_locus_summarize.main(argv)
    print ("FINISHED locus summarize")
    
def cn_summarize(envSpec):
    argv=["cn_probeset_summarize",
          "--cnps", envSpec.cnpDefsFile(),
          "--output", envSpec.cnSummarizeOut(),
          "--missing_value_label", envSpec.missingValueLabel(),
          "--normalization-probes", envSpec.normalizationProbes(),
          "--no_locus",
          "--output", envSpec.cnSummarizeOut(),
          envSpec.locusSummarizeOut()
          ]
    birdsuite.cn_probeset_summarize.main(argv)
    
    print ("FINISH CN SUMMARIZATION") 

def alignGenotypesIntensityData(envSpec):
    print ("intersecting genotypes and CNV intensity data")
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="align"
    
    #genotypesFileIn, intensityFileIn, genotypesFileOut, intensityFileOut
    dctArguments={"genotypesFileIn":envSpec.genotypeFile(),
                  "intensityFileIn":envSpec.cnSummarizeOut(),
                  "genotypesFileOut":envSpec.genotypesAligned(),
                  "intensityFileOut":envSpec.intensitiesAligned()
                  }
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
  
def QCAlignedGenotypeIntensityData(envSpec):
    genotypes=envSpec.genotypesAligned()
    intensity=envSpec.intensitiesAligned()
    genotypesOut=envSpec.genotypesAlignedQCed()
    intensityOut=envSpec.intensitiesAlignedQCed()
    cnvDefs=envSpec.cnpDefsFile()
    cnvDefsOut=envSpec.filteredCNVDefsFile()
    
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="reduceMap"
    
    dctArguments={"genotypesFileIn":genotypes,
                  "intensityFileIn":intensity,
                  "genotypesFileOut":genotypesOut,
                  "intensityFileOut":intensityOut,
                  "cnvDefsFile": cnvDefs,
                  "cnvDefsOutFile":cnvDefsOut
                  }
    
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
    #rename files if new files were created.
    #if os.path.exists(genotypesOut) and os.path.exists(intensityOut):
    #    os.rename (genotypes,genotypes+".no_fld_qc")
    #    os.rename(intensity, intensity+".no_fld_qc")
    #    os.rename(genotypesOut, genotypes)
    #    os.rename(intensityOut, intensity)
    
def splitCanaryData(envSpec):
    """Split up the filtered genotypes and intensity data into chemistry plates.  Use these sub matrixes to build "per plate priors"
    These priors will then be averaged together to produce the final set of priors."""
    
    #make a temp directory to split data into.
    canaryTestDir=envSpec.canaryTestDir()
    if not os.path.exists(canaryTestDir): os.makedirs(canaryTestDir)
    
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="splitTrainingData"
     
    dctArguments={"trainingData":envSpec.intensitiesAlignedQCed(),
                  "plateMap":envSpec.mapFile(),
                  "outDir":canaryTestDir,
                  "suffix":".probeset_summary",
                  "minNumSamples":envSpec.minNumSamples()
                  }
    
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
    dctArguments={"trainingData":envSpec.genotypesAlignedQCed(),
                  "plateMap":envSpec.mapFile(),
                  "outDir":canaryTestDir,
                  "suffix":".filteredGenotypes",
                  "minNumSamples":envSpec.minNumSamples()
                  }
    
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
        
def prep_clusters(envSpec):
    print ("START PREPPING CLUSTERS")
    canaryTestDir=envSpec.canaryTestDir()
    files=os.listdir(canaryTestDir)
    for f in files:
        if f.endswith(".probeset_summary"):
            plateName=os.path.basename(f).split(".")[0]
            prep_clusters_perPlate(plateName, envSpec)
            #runCanarySingle(f, envSpec)
          
    print ("FINISH PREPPING CLUSTERS")

def prep_clusters_perPlate(plateName, envSpec):
    print ("START PREPPING CLUSTERS PLATE: " +  plateName)
    #change genotypes and intensities
    genoF=envSpec.canaryTestDir()+"/"+plateName+".filteredGenotypes"
    
    intF=envSpec.canaryTestDir()+"/"+plateName+".probeset_summary"
    outF=envSpec.canaryTestDir()+"/"+plateName+".prepped_clusters"
    argv=['prep_clusters', 
          '--intensities', intF,
          '--genotypes', genoF,
          '--output', outF
          ]
    
    birdsuitepriors.canary.prep_clusters.main(argv)
    
    print ("FINISH PREPPING CLUSTERS PLATE: "+ plateName)

def fill_clusters(envSpec):
    print ("START FILLING CLUSTERS")
    canaryTestDir=envSpec.canaryTestDir()
    files=os.listdir(canaryTestDir)
    for f in files:
        if f.endswith(".prepped_clusters"):
            plateName=os.path.basename(f).split(".")[0]
            fill_clusters_per_plate(plateName, envSpec)
            
def fill_clusters_per_plate(plateName, envSpec):
    prepClusterSource=envSpec.canaryTestDir()+"/"+plateName+".prepped_clusters"
    outPriors=envSpec.canaryTestDir()+"/"+plateName+".priors"
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="fillClusters"
    #sourceFile, outputFile, 
    dctArguments={"sourceFile":prepClusterSource,
                  "outputFile":outPriors}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
def mergePerPlatePriors(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="mergePriors"
    
    dctArguments={"fileDirectory":envSpec.canaryTestDir(),
                  "suffix":".priors",
                  "outFile":envSpec.priorsFileWithoutQC()}

    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
def runCanary(envSpec):
  #splitCanaryData(envSpec)
  canaryTestDir=envSpec.canaryTestDir()
  files=os.listdir(canaryTestDir)
  for f in files:
      if f.endswith(".probeset_summary"):
          runCanarySingle(f, envSpec)
  
  mergeCanaryResults(".canary_calls", envSpec)
  mergeCanaryResults(".canary_confs", envSpec)
  mergeCanaryResults(".probeset_summary", envSpec)
      
def runCanarySingle (inFile, envSpec):
    lstLibraries=["broadgap.canary"]
    methodName="cnp_clustering.cluster"
    
    
    dctArguments={"profileList":envSpec.canaryTestDir()+"/"+inFile,
                  "priorsFile":envSpec.priorsFileWithoutQC(),
                  "offsetFile":envSpec.offSetFile(),
                  "outDir":envSpec.canaryTestDir()}
    
    baseName=os.path.basename(inFile)
    baseName=baseName.split(".")[0]
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

    os.rename(envSpec.canaryTestDir()+"/allData_genotypes.txt", envSpec.canaryTestDir()+"/"+baseName+".canary_calls")
    os.rename(envSpec.canaryTestDir()+"/allData_uncertainty.txt", envSpec.canaryTestDir()+"/"+baseName+".canary_confs")
    os.remove(envSpec.canaryTestDir()+"/cluster_membership.txt")
    os.remove(envSpec.canaryTestDir()+"/shiftFactor.txt")

def mergeCanaryResults (fileType, envSpec):
    
    files=os.listdir(envSpec.canaryTestDir())
    lstFiles=[]
    for f in files:
        if f.endswith(fileType): lstFiles.append(envSpec.canaryTestDir()+"/"+f)
    
    argv=["mergeMatrixes",
          "-n", "1",
          "-o", envSpec.outputFile()+fileType]
    argv.extend(lstFiles)
    mergeMatrixes.main(argv)
          
def plotCanary (envSpec):
    lstLibraries=["broadgap.cnputils"]
    methodName="cnp_graphs.graphPlateClusterAssignments"
    intensityDataFile=envSpec.outputFile()+".probeset_summary"
    assignmentDataFile=envSpec.outputFile()+".canary_calls"
    uncertaintyFile=envSpec.outputFile()+".canary_confs"
    
    priorsFile=envSpec.priorsFileWithoutQC()
    mapFile=envSpec.mapFile()
    outputFileName=envSpec.priorsFileWithoutQC()+".pdf"
    
    dctArguments={"intensityDataFile":intensityDataFile,
                  "assignmentDataFile":assignmentDataFile,
                  "uncertaintyFile":uncertaintyFile,
                  "mapFile":mapFile,
                  "outputFileName":outputFileName,
                  "priorsFile":priorsFile
                  }
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
    #cnp_graphs.graphPlateClusterAssignments(intensityDataFile, assignmentDataFile, uncertaintyFile, mapFile=mapFile, outputFileName= outputFileName, priorsFile=priorsFile)

def qcPriors(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="priorsQC"
    #priorsQC<-function (referenceIntensityFile, referenceGenotypesFile, calledGenotypeFile, calledGenotypeUncertaintyFile, priorsFile, callRateThreshold=0.85, FLDThreshold=2, concordanceThreshold=0.95)
    
    referenceIntensityFile=envSpec.intensitiesAlignedQCed()
    referenceGenotypesFile=envSpec.genotypesAlignedQCed()
    calledGenotypeFile=envSpec.outputFile()+".canary_calls"
    calledGenotypeUncertaintyFile=envSpec.outputFile()+".canary_confs"
    priorsFile=envSpec.priorsFileWithoutQC()
    mapFile=envSpec.mapFile()
    outFile=envSpec.outputFile()
    
    dctArguments={"referenceIntensityFile":referenceIntensityFile,
                  "referenceGenotypesFile":referenceGenotypesFile,
                  "calledGenotypeFile":calledGenotypeFile,
                  "calledGenotypeUncertaintyFile":calledGenotypeUncertaintyFile,
                  "priorsFile":priorsFile,
                  "plateMapFile":mapFile,
                  "outFile":outFile
                  }
    
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    #if os.path.exists(outFile):
    #    os.rename(envSpec.outputFile(), envSpec.outputFile()+".no_qc")
    #    os.rename(outFile, priorsFile)
    

def populationSpecificPriors(envSpec):
    #buildPopSpecificPriors<-function (popFile, famFile, referenceGenotypesFile, priorsFile)
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="buildPopSpecificPriors"
    popFile=envSpec.popFile()
    famFile=envSpec.famFile()
    referenceGenotypesFile=envSpec.genotypesAlignedQCed()
    priorsFile=envSpec.outputFile()
    dctArguments={"popFile":popFile,
                  "famFile":famFile,
                  "referenceGenotypesFile":referenceGenotypesFile,
                  "priorsFile":priorsFile
                  }
    
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    

def cleanupPriorsMap(envSpec):
    #buildPopSpecificPriors<-function (popFile, famFile, referenceGenotypesFile, priorsFile)
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="cleanupPriorsMap"
   
    priorsFile=envSpec.outputFile()
    originalMapFile=envSpec.filteredCNVDefsFile()
    outMapFile=envSpec.mapFileOut()
    
    dctArguments={"priorsFile":priorsFile,
                  "originalMapFile":originalMapFile,
                  "outMapFile":outMapFile
                  }
    
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

    if envSpec.offSetFile() is not None:
        methodName="cleanupOffSetFile"
        offSetFile=envSpec.offSetFile()
        
        offSetFileOut=os.path.splitext(priorsFile)[0]+".canary_offsets"
        dctArguments={"priorsFile":priorsFile,
                  "inOffsetFile":offSetFile,
                  "outOffSetFile":offSetFileOut
                  }
        RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
    #if there's no offset file, make one.
    
    if (envSpec.offSetFile()) is None:
        offSetFileOut=os.path.splitext(priorsFile)[0]+".canary_offsets"
        f = open(offSetFileOut,'w')
        f.write("cnp_id\toffset\n")
        f.close()
        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    lstSteps=[annotate_allele_summary, locus_summarize, cn_summarize, alignGenotypesIntensityData, QCAlignedGenotypeIntensityData, 
              splitCanaryData, prep_clusters,  fill_clusters, mergePerPlatePriors, runCanary, plotCanary, qcPriors, 
              populationSpecificPriors, cleanupPriorsMap]
    
    strSteps = "\n\t".join([str(i+1) + ": " + step.func_name for i, step in enumerate(lstSteps)])
    
    parser = optparse.OptionParser(usage=__doc__ + "\nSteps are: " + strSteps + "\n")
    
    parser.add_option("-b", "--basename",
                      help="""Used to name all the temp output files.""")
    
    parser.add_option("-o", "--output", dest="outputFile", default=None,
                      help="""Where to write output.  
Suggested naming scheme for priors is as follows:
chipType + "." canaryMapName + ".canary_priors"
example:
GenomeWideSNP_6.HM3.canary_priors
GenomeWideSNP_6.Conrad.canary_priors
(where canaryMapName is the source for CNV map, such as HM3, HM2, Conrad, 1KG)
                      
                      Default: stdout""")
    
    parser.add_option("-i", "--intensity_file", dest="intensityFile", default=None,
                      help="""Intensity summary file, (output using the sumz option of apt-probeset-genotype).  Can be
generated by other programs.  The first column name is probeset_id, followed by sample names.  
Each row contains the intensity information for an A or B probe for those samples (with a -A or -B 
to indicate which allele is being measured.) The A probe is always followed by the B probe for an allele. 
File is tab separated.  
                      
                      Example: 
                      
                      probeset_id     NA06985     NA06991
                      SNP_A-2131660-A 1403.81353      1175.07797
                      SNP_A-2131660-B 1507.16102      1160.32130""")
    
    parser.add_option("--genotype_file", dest="genotypeFile", default=None,
                      help="""Hapmap genotype file.  Each row is a CNV, each column an individual.  
SNPS should match the SNPs in the intensity file.  There must be a SNP here for each SNP
in the intensity file, and the same set of samples. File is tab separated.
                      
                      Example:
                      
                      probeset_id     NA06985 NA06991
                      AFFX-SNP_10000979       1       1""")

    parser.add_option("--probe_locus", dest="probe_locus",
                      help="(Required for step 1)  SNP and CN probe positions.")

    parser.add_option("--force_cn_summarization", dest="force_cn_summarization", default=False, action="store_true",
                      help="""Force summarization of CN probes if they have an A and B allele.
Optional for step 2.  Useful if you're running illumina platforms if they encode a CN probe with both A and B alleles.""")
    
    parser.add_option("-c", "--cnps", dest="cnpDefsFile", 
                      help="""Tab-separated input file with the following columns:
CNP ID, chromosome, start genomic position, end genomic position (inclusive).
Required for step 3.""")
      
    parser.add_option("-m", "--missing_value_label", dest="strMissingValueLabel", default="NaN", 
                      help="""Label of data that is missing from the platform. 
Illumina products do not always have data available for every probe/individual combination. 
Default is %default.  Required for step 3""")
    
    #--normalization-probes
    parser.add_option("--normalization-probes", dest="normalizationProbes",
                      help="""List of probes for normalizing each sample.  For each sample, find the median of 
these probes and divide the output intensity by this value.""")

    parser.add_option("--mapFile", default=None, dest="mapFile", 
                      help="""A map file that has the sample and plate information.  
Used to calculate per-plate priors which are then averaged together. 
No header, tab separated file.
                      
                      Format:
                      
                      CEL_A    SAMPLE_A    PLATE_FOO
                      CEL_B    SAMPLE_B    PLATE_FOO
                      """)
    #offSetFile
    
    parser.add_option("--mapFileOut", default=None, dest="mapFileOut", 
                      help="""A matching file for the output priors file.  
This is the original --mapFile entry, subselected for the CNVs that passed QC on this platform.

Suggested naming scheme for mapFile is as follows:
chipType + "." genome build + "." + canaryMapName + ".cnv_defs"
example:
GenomeWideSNP_6.hg18.HM3.cnv_defs
GenomeWideSNP_6.hg18.cnv_defs
(where canaryMapName is the source for CNV map, such as HM3, HM2, Conrad, 1KG)
""")

    parser.add_option("--offSetFile", dest="offSetFile", default=None,
                      help="""(OPTIONAL) A list of CNVs that have offsets.  Canary works in a 0-4 CN workspace, so if a CNV has higher CN than that [example: CN2-6], you can "add" to the integer copy number call post canary using this file.  In this example, you would shift the CN by 2. File format has a header, and is tab separated:
                      
                      cnp_id  offset
                      
                      CNVR1.6   0
                      
                      CNVR17.1  1
                      """)

    parser.add_option("--popFile", dest="popFile",
                      help="""Links samples to populations.  Used to make population specific priors.
File format is 2 columns tab separated with no header:
                      
                      GIH NA20847
                      
                      YRI NA18488
                      
                      YRI NA18519
                      """)

    parser.add_option("--famFile", dest="famFile",
                      help="""Links samples to their pedigree info.  Used to make population specific priors.
File format is at least 4 columns tab separated with no header.  This is a plink standard format.
                      
                      NA20847 NA20847 0 0 2 -9
                      
                      Y001 NA18488 0 0 2 -9
                      
                      Y014 NA18519 0 0 1 -9
                      """)

    parser.add_option("--minNumSamples", dest="minNumSamples", default=20,
                      help="""The minimum number of samples on a chemistry plate to consider it for priors.
Defaults to %default.""")
    
    parser.add_option("--tempDir", dest="tempDir", default=None,
                      help="""A temp directory to put intermediate files in.""")
    
    parser.add_option("--first_step", type="int", default=1,
                      help="""What step to start with in birdseed priors generation process.  Default: %default""")
    parser.add_option("--last_step", type="int", default=len(lstSteps),
                      help="""What step to end with in birdseed priors generation process (1-based, inclusive).  Default: %default""")
    
    parser.add_option("--verbose", dest="bVerbose", default=False, action="store_true",
                      help="""Run programs in verbose mode whenever possible""")
            
    lstRequiredOptions=['intensityFile', 'genotypeFile', 'probe_locus', 'tempDir', 'basename', 'outputFile', 'cnpDefsFile', 'mapFileOut', 'popFile']
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    if dctOptions.last_step > len(lstSteps) or dctOptions.first_step > len(lstSteps):
        parser.print_help()
        return 1
    
    
    tempDir=os.path.abspath(dctOptions.tempDir)
    
    envSpec=EnvironmentSpec(dctOptions.intensityFile, dctOptions.genotypeFile, 
                            dctOptions.probe_locus, tempDir, 
                            dctOptions.basename, dctOptions.outputFile, 
                            dctOptions.force_cn_summarization, dctOptions.cnpDefsFile, 
                            dctOptions.strMissingValueLabel, dctOptions.normalizationProbes,
                            dctOptions.mapFile, dctOptions.offSetFile, 
                            dctOptions.minNumSamples, 
                            dctOptions.popFile, dctOptions.famFile, dctOptions.mapFileOut,
                            dctOptions.bVerbose)
    
    
    
    if not os.path.exists(tempDir): os.makedirs(tempDir)
    
    outFile=dctOptions.outputFile
    outFile=os.path.abspath(outFile)
    outDir=os.path.split(outFile)[0]
    if not os.path.exists(outDir): os.makedirs(outDir)
    
    for step in lstSteps[dctOptions.first_step-1:dctOptions.last_step]:
        print ("Running step: " + step.func_name)
        step(envSpec)
        print ("Finished step: " + step.func_name)

    print ("Canary priors creation FINISHED!")
    
if __name__ == "__main__":
    sys.exit(main())