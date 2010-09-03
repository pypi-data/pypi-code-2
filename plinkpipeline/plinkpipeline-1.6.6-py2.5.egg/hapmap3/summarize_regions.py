import os, sys, optparse

from hapmap3 import sangerFormat_to_annotatedSummary
from birdsuite import cn_locus_summarize
from birdsuite import cn_probeset_summarize
from mpgutils import mergeMatrixes
from mpgutils import utils

def setupTempDir (tempDir):
    if os.path.exists(tempDir) is False:
        os.mkdir(tempDir)
        
def getPlates (plateFile):
    lstPlates=[]
    fIn = open(plateFile)
    strLine = None
    for strLine in fIn:
        lstPlates.append(strLine.rstrip("\n"))
    return lstPlates

def findFile (plateName, dataDir, chromosome):
    """Returns the full path name of a file if found or None if not found"""
    lstFiles=os.listdir(dataDir)
    strFileToFind=plateName+"_"+chromosome+".dat"
    for f in lstFiles:
        if f==strFileToFind:
            return os.path.join(dataDir, f)
    return None
    
def toAnnotatedSummary (dataDir, tempDir, lstPlates, missingValueLabel, intensityMultiplier, bVerbose=False):
    print ("Annotating summary files")
    lstChromosomes=range(1,23)
    for plate in lstPlates:
        lstFiles=[findFile(plate, dataDir, "chr"+str(chr)) for chr in lstChromosomes]
        
        #longer code so that missing files are dealt with appropriately.
        lstFilesFixed=[]
        for f in lstFiles: 
            if f is not None: lstFilesFixed.append(f)
        
        if (bVerbose): 
            print ("Processing plate " + plate +" found " + str (len(lstFilesFixed)) + " chromosome files to use")
                
        if len(lstFilesFixed)>0:
            outFile=os.path.join(tempDir, plate+".annotated_summary")
            lstArgs=['sangerFormat_to_annotatedSummary',
                     '--missing_value_label='+missingValueLabel, 
                     '--intensity_multiplier='+intensityMultiplier,
                     '--output='+outFile]
            lstArgs.extend(lstFilesFixed)
            if bVerbose: print (" ".join(lstArgs))
            sangerFormat_to_annotatedSummary.main(lstArgs)

def toLocusSummary (tempDir, lstPlates, bVerbose=False):
    
    for plate in lstPlates:
        print ("Generating Locus Summary files for plate " + plate)
        inFile=os.path.join(tempDir, plate+".annotated_summary")
        outFile=os.path.join(tempDir, plate+".locus_summary")
        lstArgs=['cn_locus_summarize', 
                 '--output='+outFile,
                 '--force_cn_summarization',
                 inFile]
        if bVerbose: print (" ".join(lstArgs))
        cn_locus_summarize.main(lstArgs)
        
def toSummarizedProbeset (tempDir, lstPlates, regions, algorithm, normalizationProbes, bVerbose=False):
    
    for plate in lstPlates:
        print ("Generating CNV summary files for plate " +plate)
        inFile=os.path.join(tempDir, plate+".locus_summary")
        outFile=os.path.join(tempDir, plate+"."+algorithm)
        lstArgs=['cn_probeset_summarize', 
                 '--cnps='+regions,
                 '--algorithm='+algorithm,
                 '--no_locus', 
                 '--output='+outFile]
        if normalizationProbes is not None:
            lstArgs.append('--normalization-probes='+normalizationProbes)
        lstArgs.append(inFile)
        if bVerbose: print (" ".join(lstArgs))
        cn_probeset_summarize.main(lstArgs)

def mergeSummarizedProbesets (tempDir, lstPlates, output, algorithm, bVerbose=False):
    print ("Merging CNV summary files")
    lstInFiles=[]
    for plate in lstPlates:
        inFile=os.path.join(tempDir, plate+"."+algorithm)
        lstInFiles.append(inFile)
    
    
    lstArgs=['mergeMatrixes',
             '--output='+output]
    lstArgs.extend(lstInFiles)
    if bVerbose: print (" ".join(lstArgs))
    mergeMatrixes.main(lstArgs)
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", dest="output",
                      help="""(Required) Where to write output file.""")
    
    parser.add_option("--algorithm", dest="algorithm", default="medpolish-exp",
                      help="""Which algorithm to summarize with. Default: medpolish-exp""")
    
    parser.add_option("--plateFile", dest="plateFile", 
                      help="""(Required) PlateFile is a list of plates to process, has no header and 1 column.""")
    
    parser.add_option("--dataDir", dest="dataDir", 
                      help="""(Required) The directory where the exchange format files are located. 
                      Example file: hapmap3_intensities_1M_p47576_chr10.dat""")
    
    parser.add_option("--regions", dest="regions", 
                      help="""(Required) A file describing the regions to summarize.  
                      This has 4 columns (with header)
                      cnp_id, chr, start, end.
                      It follows the CNV map file format described by cn_probeset_summarize""")
    
    parser.add_option("--normalizationProbes", dest="normalizationProbes", default=None,
                      help="""The normalization probes file.  See: cn_probeset_summarize.""")
    
    parser.add_option("--tempDir", dest="tempDir",
                      help="""(Required) Where to put intermediate temp files.""")
    
    parser.add_option("--startAtSummarization", dest="sumFlag", action="store_true", default=False,
                      help="""Should the process skip annotation and locus summarization, and start with CNV probeset summarization?
                      You can do this if you've run the entire pipeline on a data set once, and wish to process with a different map/algorithm.""")
    
    parser.add_option("-m", "--missing_value_label", dest="missingValueLabel", default="-1",
                      help="""Encode this value in the canonical missing value label (-1)""")
    
    parser.add_option("-i", "--intensity_multiplier", dest="intensityMultiplier", default="1",
                      help="""What to multiply intensity by to make it similar to other data sets. 
                      Defaults to 1 (no change)""")
    
    parser.add_option("-v", "--verbose", dest="bVerbose", default=False, action="store_true", 
                      help="""Run in verbose mode""")
    
    lstRequiredOptions=['plateFile', 'output', 'dataDir', 'regions', 'tempDir']
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    setupTempDir(dctOptions.tempDir)
    lstPlates=getPlates(dctOptions.plateFile)
    bVerbose=dctOptions.bVerbose
    
    if dctOptions.sumFlag == False:
        toAnnotatedSummary (dctOptions.dataDir, dctOptions.tempDir, lstPlates, 
                            dctOptions.missingValueLabel, dctOptions.intensityMultiplier, bVerbose=bVerbose)
        toLocusSummary (dctOptions.tempDir, lstPlates, bVerbose=bVerbose)
    else:
        print ("SKIPPING annotation and locus summarization")
        
    toSummarizedProbeset (dctOptions.tempDir, lstPlates, dctOptions.regions, dctOptions.algorithm, dctOptions.normalizationProbes, bVerbose=bVerbose)
    mergeSummarizedProbesets (dctOptions.tempDir, lstPlates, dctOptions.output, dctOptions.algorithm, bVerbose=bVerbose)
    
if __name__ == "__main__":
    sys.exit(main())
        