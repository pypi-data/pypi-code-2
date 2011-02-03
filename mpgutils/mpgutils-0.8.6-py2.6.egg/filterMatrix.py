'''
Created on Jun 9, 2009

@author: nemesh
'''
import optparse
import sys
import string
from mpgutils import utils
import mpgutils.fk_utils as fk


def readOrderedFilterFile (filterFile):
    if filterFile is None: return None
    print "reading in filter file..."
    #.strip()
    result=[]
    fIn= open (filterFile, "r")
    counter=0
    for strLine in fIn:
        strLine=strLine.strip()
        result.append(strLine)
        counter=counter+1
        if (counter%10000==0): print str(counter)
    return (result)

def readFilterFile (filterFile):
    if filterFile is None: return None
    print "reading in filter file..."
    #.strip()
    result=set()
    
    fIn= open (filterFile, "r")
    counter=0
    for strLine in fIn:
        strLine=strLine.strip()
        #if strLine not in result:
            #result.append(strLine)
        result.add(strLine)
        counter=counter+1
        if (counter%10000==0): print str(counter)
        
    return frozenset(result)
                            
def filterMatrix(strInFile, strRowFile, strColFile, strOutFileName, outFileDelimiter='\t'):
    
    rowsToKeep=readFilterFile(strRowFile)
    colsToKeep=readOrderedFilterFile(strColFile)
    fIn= open (strInFile, "r")
    out=open(strOutFileName, 'w')
    
    strHeader=fIn.readline()
    lstHeader = strHeader.split()
    
    if colsToKeep is not None :
        colsToKeep=fk.intersect(colsToKeep, lstHeader)
        colIdx = [lstHeader.index(e) for e in colsToKeep]
        newHeader=outFileDelimiter.join(fk.arbslice(lstHeader, colIdx))+"\n"
    else:
        newHeader=strHeader
    out.write(newHeader)
    counter=0
    print "Writing filtered output (1 dot per 10000 entries scanned)"
    for strLine in fIn:
        
        if colsToKeep is not None :
            lstLine=strLine.split()
            lstNewLine=outFileDelimiter.join(fk.arbslice(lstLine, colIdx))+"\n"
        else:
            lstLine=strLine.split(None,1)
            lstNewLine=strLine
        
        rowID=lstLine[0]
        
        if rowsToKeep is None or (rowsToKeep is not None and rowID in rowsToKeep):    
            out.write(lstNewLine)
        counter=counter+1
        if counter%10000==0: print ".",
    out.close()
    return True
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", default=None, dest="output",
                      help="""(Required) Output a single calls or confs file that 
                      is the result of merging multiple calls/confs files""")
    
    parser.add_option("-r", "--rowsFile", default=None, dest="rowFile", 
                      help="""(Optional) A file listing the rows to retain in this matrix.
                        These correspond to the 1st column of the matrix (not including the header).""")
    
    parser.add_option("-c", "--columnFile", default=None, dest="colFile",
                      help="""(Optional) A file listing the columns to retain in this matrix.
                        These correspond to the header line (1st line) of input matrix""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=["output"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions) or len(lstArgs) <2:
        parser.print_help()
        return 1
    
    file = lstArgs[1]
    successFlag=filterMatrix(file, dctOptions.rowFile, dctOptions.colFile, dctOptions.output)
    
    if successFlag: print ("Finished Filter Successfully")
    
if __name__ == "__main__":
    sys.exit(main())