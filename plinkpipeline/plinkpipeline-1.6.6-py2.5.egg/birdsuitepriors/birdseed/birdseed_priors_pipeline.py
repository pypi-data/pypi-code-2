'''

Create birdseed priors from a set of intensity information and genotypes.  The samples and SNPs in the intensity
file and genotypes must overlap - the intensity probes can be a subset of the genotypes, but the samlples in both sets must be
a complete overlap.


Created on Aug 27, 2009

@author: nemesh
'''
import optparse
import os
import sys
import mpgutils.utils as utils
import mpgutils.filterMatrix as filterMatrix
import mpgutils.fk_utils as fk_utils
from mpgutils.RUtils import RscriptToPython
from birdsuitepriors.birdseed import sumz_reformat
from birdsuitepriors.birdseed import stitch
from birdsuitepriors.birdseed import fixpriors

class EnvironmentSpec(object):
    def __init__(self, intensityFile, genotypeFile, hapmapGenderFile, specialSNPsFile, strMissingValueLabel, tempDir, outputFile):
        self._intensityFile = intensityFile
        self._genotypeFile = genotypeFile
        self._hapmapGenderFile = hapmapGenderFile
        self._strMissingValueLabel=strMissingValueLabel
        self._specialSNPsFile = specialSNPsFile
        self._tempDir = tempDir
        self._outputFile = outputFile

    def intensityFile(self):
        return self._intensityFile

    def genotypeFile(self):
        return self._genotypeFile
    
    def filteredGenotypeFile(self):
       #return self._tempDir + "/genotypeRowNames.txt"
        return self._tempDir+ "/filteredGenotypes.txt"
    
    def hapmapGenderFile(self):
        return self._hapmapGenderFile
    
    def strMissingValueLabel(self):
        return self._strMissingValueLabel
    
    def specialSNPsFile(self):
        return self._specialSNPsFile
    
    def tempDir(self):
        return self._tempDir
    
    def outputFile(self):
        return self._outputFile
    
    def sumZFile(self):
        if self._tempDir is not None :
            return (self._tempDir+"/birdseed.sumz")

def subselect(envSpec):
    print "Filtering genotype data..."
    rowsIntensity=set()
    counter=0
    print "reading in SNP names from intensity file"
    f = open(envSpec.intensityFile())
    for line in f:
        counter=counter+1
        if (counter%10000==0): print str(counter)
        line = line.split(None,1)
        #if line[0]=='rs9999963-A':
        #    print("STOP")
            
        snp=line[0][0:-2]
        appender=line[0][-2:]
        if appender=="-A": rowsIntensity.add(snp)
    
    f.close()
    genoRowNamesFile=envSpec.tempDir()+"/genotypeRowNames.txt"
    out=open (genoRowNamesFile, "w")
    out.write("probeset_id"+"\n")
    
    for r in rowsIntensity:
        out.write(r +"\n")
    out.close()
    print ("writing reduced matrix")
    
    filterMatrix.filterMatrix(envSpec.genotypeFile(), genoRowNamesFile, None, envSpec.filteredGenotypeFile(), "\t")
    
    rowsGenotype=set()
    f = open(envSpec.filteredGenotypeFile())
    for line in f:
        rowsGenotype.add(line.split(None,1)[0])
    
    diff=rowsIntensity.difference(rowsGenotype)
    if len(diff) >0:
        print"\nFound " + str(len(diff)) + " SNPs missing genotype information:"
        print (str(diff))
        print"\nSince I found " + str(len(diff)) + " SNPs missing genotype information, I can't continue"
        sys.exit(1)
        
def reformat(envSpec):
    sumz_reformat.writeSumZ(envSpec.intensityFile(), envSpec.strMissingValueLabel(), envSpec.filteredGenotypeFile(), envSpec.hapmapGenderFile(), envSpec.sumZFile())
    
def summarizeSNPs(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="summarizeSNPs"
    dctArguments={"inputThetasFile":envSpec.sumZFile(),
                  "specialSNPsFile":envSpec.specialSNPsFile(),
                  "outFileDir":envSpec.tempDir()}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    
    
def autoseeds(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="auto_seeds"
    dctArguments={"sourceFile":envSpec.tempDir()+"/auto_snps.priors",
                  "outFileDir":envSpec.tempDir()}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

def mitoseeds(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="mito_seeds"
    dctArguments={"sourceFile":envSpec.tempDir()+"/mito_snps.priors",
                  "outFileDir":envSpec.tempDir()}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

def xchrseeds(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="xchr_seeds"
    dctArguments={"sourceFile":envSpec.tempDir()+"/xchr_snps.priors",
                  "outFileDir":envSpec.tempDir()}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

def ychrseeds(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="ychr_seeds"
    dctArguments={"sourceFile":envSpec.tempDir()+"/ychr_snps.priors",
                  "outFileDir":envSpec.tempDir()}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

def stichResults(envSpec):
    stitch.stitch(envSpec.tempDir(), envSpec.tempDir()+"/all_snps.seeds")
    
def fixPriors (envSpec):
    fixpriors.fixpriors(envSpec.tempDir()+"/all_snps.seeds", envSpec.outputFile() )


                        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    lstSteps=[subselect, reformat, summarizeSNPs, autoseeds, mitoseeds, xchrseeds, ychrseeds, stichResults, fixPriors]
    
    strSteps = "\n\t".join([str(i+1) + ": " + step.func_name for i, step in enumerate(lstSteps)])
    
    parser = optparse.OptionParser(usage=__doc__ + "\nSteps are: " + strSteps + "\n")
     
    parser.add_option("-o", "--output", dest="outputFile", default=None,
                      help="""Where to write output.  Default: stdout""")
    
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
                      help="""Hapmap genotype file.  Each row is a SNP, each column an individual.  
                      SNPS should match the SNPs in the intensity file.  There must be a SNP here for each SNP
                      in the intensity file, and the same set of samples. File is tab separated.
                      
                      Example:
                      
                      probeset_id     NA06985 NA06991
                      AFFX-SNP_10000979       1       1""")
    
    parser.add_option("--genderFile", dest="hapmapGenderFile", default=None,
                      help="""Hapmap gender file.  Contains two columns, the sample ID, and a 1 for males, 2 for females.  The file is tab seperated.
                      
                      Example:
                      
                      sampleID        gender
                      
                      NA12003         1
                      
                      NA12004         2
""") 

    parser.add_option("--specialSNPsFile", dest="specialSNPsFile", default=None,
                      help="""A file that details SNPs that aren't copy number 2 in both males and females.  This covers
                      the X, Y, PAR, and mitochondria SNPs. File is tab separated.
                      
                      Example:
                      
                      probeset_id     chr     copy_male       copy_female
                      SNP_A-8574947   MT      1       1
                      SNP_A-4261602   PAR     2       2
                      SNP_A-8524777   X       1       2
                      SNP_A-8290281    Y    1    0""")

    parser.add_option("-m", "--missing_value_label", dest="strMissingValueLabel", default="NaN", 
                      help="""Label of data that is missing from the platform. 
Illumina products do not always have data available for every probe/individual combination. 
Default is %default.""")


    parser.add_option("--tempDir", dest="tempDir", default=None,
                      help="""A temp directory to put intermediate files in.""")
    
    parser.add_option("--first_step", type="int", default=1,
                      help="""What step to start with in birdseed priors generation process.  Default: %default""")
    parser.add_option("--last_step", type="int", default=len(lstSteps),
                      help="""What step to end with in birdseed priors generation process (1-based, inclusive).  Default: %default""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    lstRequiredOptions=['outputFile', 'intensityFile', 'genotypeFile', 'hapmapGenderFile', 'specialSNPsFile', 'tempDir']
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    envSpec=EnvironmentSpec(dctOptions.intensityFile, dctOptions.genotypeFile, dctOptions.hapmapGenderFile, dctOptions.specialSNPsFile, dctOptions.strMissingValueLabel, dctOptions.tempDir, dctOptions.outputFile)
    
    if not os.path.exists(dctOptions.tempDir): os.makedirs(dctOptions.tempDir)
    
    for step in lstSteps[dctOptions.first_step-1:dctOptions.last_step]:
        print ("Running step: " + step.func_name)
        step(envSpec)
        print ("Finished step: " + step.func_name)

if __name__ == "__main__":
    sys.exit(main())