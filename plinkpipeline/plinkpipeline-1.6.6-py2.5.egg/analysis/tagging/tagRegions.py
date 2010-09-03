'''
Created on Jun 19, 2009

@author: nemesh
'''

from mpgutils.RUtils import RscriptToPython

import sys
import optparse
import string

from mpgutils import utils
from mpgutils.RUtils import RscriptToPython
from mpgutils.OptParseExtensions import IndentedHelpFormatterWithNL

def getFilters(lstLibraries):
        methodName="df.printFilters"
        dctArguments={}
        filters=RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=True, bVerbose=False)
        filters=filters.strip()
        filters=filters.split("\n")
        filterString="\n".join(filters)+"\n"
        return (filterString)
    
def getPairTests(lstLibraries):
    methodName="sprt.printTests"
    dctArguments={}
    filters=RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=True, bVerbose=False)
    filters=filters.strip()
    #filters=filters.split("\n")
    #filterString="\n".join(filters)+"\n"
    return (filters)
    
def getSingleTests(lstLibraries):
    methodName="srt.printTests"
    dctArguments={}
    filters=RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=True, bVerbose=False)
    filters=filters.strip()
    filters=filters.split("\n")
    filterString="\n".join(filters)+"\n"
    return (filterString)
    
def getRegionTests(lstLibraries):
    methodName="rt.printTests"
    dctArguments={}
    filters=RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=True, bVerbose=False)
    table = ''.join(' ' if (n < 32 or n > 126) and n!=10 else chr(n) for n in xrange(256))
    filters=string.translate(filters,table) 
    filters=filters.strip()
    filters=filters.split("\n")
    filterString="\n".join(filters)+"\n"
    return (filterString)
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
   
    lstLibraries=["broadgap.hapmaptools"]
   
    parser = optparse.OptionParser(usage=__doc__, formatter=IndentedHelpFormatterWithNL())
    
    parser.add_option("--dataSet1", dest="dataSet1",
                      help="""Data set 1 input file.  Matrix with samples in columns and loci in rows.""")
    
    parser.add_option("--dataSet1Encoding", dest="dataSet1Encoding",
                      help="""The encoding used for dataSet1.  This string defines the columns in the input file that will be used by this program. 
Columns that MUST be annotated include: 
chr -  The chromosome the locus is on.
start - The start (5') genomic position of the locus
end - The  end (3') genomic position of the locus
data - The first column that contains data.  
It's assumed all columns after that have data.
OPTIONAL FIELDS:
id -  the name of the locus
comment - any comment column you wish to retain in the output, such as a quality score.  Multiple comment fields are allowed.
If the locus is a single base long, the start and end fields can point to the same position in the file.
Each field is encoded as the type followed by a ":" then the column position (columns positions start at 1).  Each field is separated by a comma.
An example:--dataSet1Encoding=id:1,chr:2,start:3,end:4,data:5""")
    
    parser.add_option("--dataSet2", dest="dataSet2",
                       help="""Data set 2 input file.  Matrix with samples in columns and loci in rows.""")
    
    parser.add_option("--dataSet2Encoding", dest="dataSet2Encoding",
                      help="""Same encoding scheme as Dataset1""")
    
    parser.add_option("--outFile", dest="outFile", 
                      help="""Where to put output results.""")

    parser.add_option("--window", dest="window", default=20000, type="int",
                      help="""How far to search into the test data set on each side of the regions to be tagged. For example, if tagging CNVs with SNP data, look at SNPs on 20000 bp window to each side of the CNV.  DEFAULT: 20000""")

    parser.add_option("--excludeOverlaps", dest="excludeOverlaps", action="store_true", default=False,
                      help="""Should regions in the two data sets that overlap be analyzed?  If this is set to true, regions that are overlapping will not be in the final output.""")

    parser.add_option("--partitionSize", dest="partitionSize", default=1000000, type="int",
                      help="""Controls how much data is loaded for each round of testing.  This partitions both the items being tagged and the items they are tagged by.  Setting this appropriately can speed up search time, as each item to be tagged needs to find all it's possible tagging elements within the search space. DEFAULT: 1000000 bp.""")

    parser.add_option("--chunkSize", dest="chunkSize", default=1000, type="int",
                      help="""Controls how many lines of data are read in from files.  This and partition size control the amount of memory used by the program. DEFAULT:1000""")

    tests=getPairTests(lstLibraries)
    
    parser.add_option("--pairedTests", dest="strPairedTests",
                      help="""Add tests you wish to run against each 2 sets of data.  For example, if analyzing a CNV and many SNPs, run this test against each CNV and the SNPs near the CNV. If you want to run more than 1 test, separate them with commas:--pairedTest=cor,rsq\nSupported Tests:\n""" + tests)
    
    parser.add_option("--pairedPermutations", dest="numPermutations", default=0, type="int",
                      help="""For paired tests, how many permutations should be run to compute pvalues?  If this option is selected, empiric pvalues of the pairedTest result will also be output.""")
    
    tests=getSingleTests(lstLibraries)
    
    parser.add_option("--dataSet1Tests", dest="dataSet1Tests",
                      help="""Tests to apply to each row of data set 1.\nSupported Tests:\n""" + tests)
    
    parser.add_option("--dataSet2Tests", dest="dataSet2Tests",
                      help="""Tests to apply to each row of data set 2.\nSupported Tests:\n""" + tests)
    
    tests=getRegionTests(lstLibraries)
    
    parser.add_option("--regionTests", dest="strRegionTests",
                      help="""Tests to apply to each row of data set 1 against all rows of data set two that overlap it.\nSupported Tests:\n""" + tests)
    
    filters=getFilters(lstLibraries)
    
    parser.add_option("--filters", dest="strFilters",
                      help='Add filter string here.  Filter strings are in the format [column name]:[filter name]:[threshold].  The column name can be any column in the output, such as any test that has been run.  If the filter selected does not require a threshold (such as NA), it can be ignored. An example filter is: \'rsq:gte:0.8\n\', which would read as "retain all R^2 values greater than or equal to 0.8.  Available filters are:\n' + filters +"\n" +"These filters are applied after all calculations are performed.")
    
    parser.add_option("--prePermutationFilters", dest="strPerPermutationFilters",
                      help='Add filter string here.  Filter strings are in the format [column name]:[filter name]:[threshold].  The column name can be any column in the output, such as any test that has been run.  If the filter selected does not require a threshold (such as NA), it can be ignored. An example filter is: \'rsq:gte:0.8\n\', which would read as "retain all R^2 values greater than or equal to 0.8.  Available filters are:\n' + filters +"\n" +"These filters are applied after all calculations are performed.")
    
    parser.add_option("--richOutput", dest="bRichOutput", action="store_true", default=False,
                      help="""Should output include full position information for DS1 and DS2?  If not set, only ID's are reported.""")
    
    parser.add_option("--verbose", dest="bVerbose", action="store_true", default=False,
                      help="""Print out lots of progress information.""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    lstRequiredOptions=["dataSet1", "dataSet1Encoding", "dataSet2", "dataSet2Encoding", "outFile"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
        #(, dataSet2, dataSet2Encoding, outFile, window=20000, partitionSize=1000000, excludeOverlap=T, listDS1TestStrings=NULL, listDS2TestStrings=NULL, listTestStrings=NULL, listFilterStrings=NULL, listPerPermutationFilterStrings=NULL, nPermutations=0, regionTestStrings, richOutput=F, verbose=F, chunkSize=10000)
    dctArguments={"dataSet1":dctOptions.dataSet1,
                  "dataSet1Encoding":dctOptions.dataSet1Encoding,
                  "dataSet2":dctOptions.dataSet2,
                  "dataSet2Encoding":dctOptions.dataSet2Encoding,
                  "outFile":dctOptions.outFile,
                  "window":dctOptions.window,
                  "partitionSize":dctOptions.partitionSize,
                  "excludeOverlap":dctOptions.excludeOverlaps,
                  "listDS1TestStrings":dctOptions.dataSet1Tests,
                  "listDS2TestStrings":dctOptions.dataSet2Tests,
                  "listTestStrings":dctOptions.strPairedTests,
                  "listFilterStrings":dctOptions.strFilters,
                  "listPerPermutationFilterStrings":dctOptions.strPerPermutationFilters,
                  "nPermutations":dctOptions.numPermutations,
                  "regionTestStrings":dctOptions.strRegionTests,
                  "richOutput":dctOptions.bRichOutput,
                  "verbose":dctOptions.bVerbose,
                  "chunkSize":dctOptions.chunkSize
    }
        
    methodName="tagCNVBySNPs"
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)

if __name__ == "__main__":
    sys.exit(main())
    
