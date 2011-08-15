import os,sys,tarfile
import zipfile
import gzip
import bz2

def checkForZip(fileName):
    supportedExtension=["zip", "gzip", "gz", "bz2"]
    
    try:
        fileName=filter(os.path.exists, ['.'.join([fileName, ext]) for ext in supportedExtension])[0]
    except:
        pass

    return fileName
    
def readFile(fileName, mode="rU"):
    if (zipfile.is_zipfile(fileName)):
       zfile = zipfile.ZipFile( fileName, mode );
       if (len(zfile.infolist()) == 1):
            return zfile.open(zfile.infolist()[0].filename, mode); #grab the first thing in there
       else : raise IOError("Only a zip file containing one item is accepted this contained :"+len(zfile.infolist()))
    elif (fileName.endswith(".tar") & tarfile.is_tarfile(fileName)):
        return tarfile.open(fileName, mode)
    elif (fileName.endswith(".gzip") or fileName.endswith(".gz")):
        return gzip.GzipFile(fileName , mode)
    elif (fileName.endswith(".bz2")):
        return bz2.BZ2File(fileName, mode)
    else:
        return open(fileName, mode)

def createDir(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except : pass


