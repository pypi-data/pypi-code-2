"""Zipblob: An utility module for working with directory-like zipped archive objects. 

Zipblob provides a data object for storing and transmitting file and directory
bundles easily. When transmitted, a Zipblob is treated as a zipfile. When
operated, Zipblob can be opened in terms of a temporal directory for free
manipulating.

For copyright information and licensing, see LICENSE.txt

Typical scenarios for using Zipblob go as follows:

# Example 1: Create an empty ZipBlob from scratch and add files:
 
b = Zipblob()
b.add_file("work/output.xml", "sub/index.html") # add work/output.xml as sub/index.html  
b.add_dir("work/data") # add whole dir
b.add_file("newlogo.jpg", "jpg/logo.jpg", "w") # add jpg/logo.jpg (replace existing, if any)

# Example 2: Make a copy of a Zipblob (just to make an example):  

c = Zipblob()
c.write(b.read())

# Example 3: Open Zipblob as a directory, for manipulation:

from wille import zipblob
import os

tmp = zipblob.Zipblob()
dir = tmp.check_out()

# Work with files found at dir (string path) ...
# Remember to delete file handles pointing to dir, otherwise check_in will cause IoError 
# (Permission denied)

file = dir + '/' + 'output.html'
file = os.path.abspath(file)

f = open(file, "w")
f.write("foo")
f.close
del f # IMPORTANT!

tmp.check_in() Note that tmp.check_in(commit=False) would discard changes 

# Example 3: Export as a zipfile:  

f = open("deploy/out.zip","wb")
f.write(c.read())
f.close()

# Example 4: Read Zipblob from a zipfile:

d = Zipblob()
f = open("deploy/out.zip","rb")
d.write(f.read()) # Another way, using built-in class wrapping: d.wrapper_write(f.wrapper_read())   
close f

# Example 5: Modify a single file (source.txt):  

f = open("data.tmp","w")
f.write(c.read_file("doc/source.txt","r"))
f.close()
# Process data.tmp ...
# Update Zipblob
c.add_file("data.tmp", "doc/source.txt", "w") 
# Finished (remove data.tmp if needed).
   
# Example 6: Work with Zipblob directly via the zipfile module and the ZipFile class:  

zipfilename = d.get_zipfile_name()
zip = zipfile.ZipFile(zipfilename, "r")
# Work with zipfile called zip directly using the mehthods of the 
# zipfile module...
zip.close()
  
The main limitation (due zipfiles) is that Zipblob can not include empty
directories. (An empty directory is simply lost when zipped.)  
    
Zipblob was originally developed for transmitting data in a visualisation 
pipeline. Note: Some applications might agree upon a common manifest file, 
e.g. for transmitting information about the contents of the Zipblob (such as
the name of the default index file).
"""

import tempfile
import os
import os.path
import zipfile
import shutil

class ZipblobWrapper:
    "A wrapper class for passing raw data (string) objects."
    
    def __init__(self, value = None, type = None):
        self.__value = value
        self.__type  = type
        
    def set_value(self, value):
        self.__value = value

    def set_type(self, type):
        self.__type  = type
        
    def get_value(self):
        return self.__value

    def get_type(self):
        return self.__type


class Zipblob: 
    "Wille Visualisation archive structure based on zipfiles."
    
    def __initialise(self, debug=False):
        "Sets up the temp dirs/files and the zip file."
        
        # Debug mode
        self.debug = debug
        
        # Create temp zipfile
        self.tmpZipFilename = None
        (fid, self.tmpZipFilename) = tempfile.mkstemp("_zipblob.zip")
        if self.debug: print(fid, self.tmpZipFilename)
        # fid needs to be close before manipulating it
        os.close(fid)

        # Create a new zipfile       
        self.zip = zipfile.ZipFile(self.tmpZipFilename, "w", zipfile.ZIP_DEFLATED)
        self.zip.close()
        self.first_file = True
        self.tempDir = None        
        
        # Add empty manifest file...
        # Discarded: manifest files are application-specific and should not
        # be endorsed on the level of the packaging utility.
        
        # Location of the temp dir when opened

    def __finalise(self):
        "Cleans up temp dirs/files and zip file."
        os.remove(self.tmpZipFilename) # Remove temp zipfile
        # If exit with open WVBlob, remove tempDir
        if self.tempDir != None:
            self.check_in(commit=False)  
        
    def __init__(self, debug=False):
		self.debug = debug
		self.__initialise()
		if self.debug: print("Initialised " + str(self))

    def __del__(self):
        self.__finalise()
        if self.debug: print("Finalised " + str(self))
    
    def __str__(self):
        return self.read()

    def set_debug_info(self, setting=True):
        "Debug mode (True/False)?"
        self.debug = setting

    def add_file(self, sourcefile, destname, mode="a"):
        "Adds file sourcefile to the Zipblob zip with the name destname."
        
        if self.first_file:
        	# Workaround for python<2.6
        	mode="w"
        	self.first_file = False        
        
        self.zip = zipfile.ZipFile(self.tmpZipFilename, mode, zipfile.ZIP_DEFLATED)
        self.zip.write(sourcefile, destname)
        self.zip.close()
        if self.debug: print("Added file " + destname)
        
    def add_dir(self, top):
        "Adds directory with relative names. (Empty dirs will not be added.)"
        os.path.walk(top, self.__visit, top)                

    def __visit(self, top, dirname, names):
        "Adds files. (Called recursively by os.walk from self.addDir.)" 
        n = len(os.path.abspath(top))
        for name in names:
            fname = os.path.join(dirname, name)
            fname = os.path.abspath(fname)
            #print("DIR: " + fname)
            if not os.path.isfile(fname): continue
            
            # strip beginning of abs path from filename 
            relname = fname[(n+1):]
            self.add_file(fname, relname, "a")

    def ok(self):
        "Checks whether Zipblob is ok or corrupted."
        return zipfile.is_zipfile(self.tmpZipFilename)

    def wrapper_read(self):
        "Returns *the entire* contents as a zipfile in using the Wrapper class."
        return ZipblobWrapper(self.read())

    def wrapper_write(self, wrapdata):
        "Writes *the entire* contents as a zipfile using the Wrapper class."
        self.write(wrapdata.get_value())

    def read(self):
        "Returns *the entire* contents as a zipfile in binary format."
        f = open(self.tmpZipFilename,"rb")
        data = f.read()
        f.close()
        return data

    def write(self, data):
        "Writes *the entire* contents as a zipfile in binary format."
        f = open(self.tmpZipFilename,"wb")
        f.write(data)
        f.close()        

    def get_zipfile_name(self):
        "Returns the filename of the temp zip file. (File is removed upon finalisation.)"
        return self.tmpZipFilename

    def read_file(self, name, mode):
        "Retrieves the contents of an individual file from the zipBlob. If name=None, returns the first file."
        zip = zipfile.ZipFile(self.tmpZipFilename, mode)
        if name==None: 
            name = self.zip.namelist()[0]
        data = zip.read(name)
        zip.close()
        return data
        
    def __dir_cmp(self, x, y):
        return len(x)-len(y)

    def check_out(self):
        "Returns Zipblob as a temporal directory. Close after use with check_in() -- note that the zipfile is not modified until check_in() is invoked."
        # Create temp dir
        self.tempDir = tempfile.mkdtemp("_zipblob_tmp")                
        if self.debug: print("TMP DIR = " + self.tempDir)        
        self.zip = zipfile.ZipFile(self.tmpZipFilename, "r")
        
        if self.debug: print("ZIP contents:")
        
        # Get zip contents... First, make directories
        dirs = []
        for n in self.zip.namelist():
            fn = self.tempDir + "/" + n
            fn = os.path.abspath(fn)
            dirs.append(os.path.dirname(fn))            
        dirs.sort(self.__dir_cmp) # create directories starting from the relative root        
        for n in dirs: 
            if self.debug: print("       " + n)
            try:
                os.makedirs(n)
            except OSError:
                pass # print("OS error: ")
        
        # Copy files to directories
        for n in self.zip.namelist():
            bytes = self.zip.read(n)
            fn = self.tempDir + "/" + n
            fn = os.path.abspath(fn)
            f = open(fn,"w")
            f.write(bytes)
            f.close()
             
        self.zip.close()

        return self.tempDir
        
    def check_in(self, commit=True):
        "Closes Zipblob after use. Setting commit=False will discard any changes."
        if self.tempDir == None: return # Not open!
        if commit:
            # Replace contents: clear old zipfile, add working dir to it
            self.zip = zipfile.ZipFile(self.tmpZipFilename, "w", zipfile.ZIP_DEFLATED)
            self.zip.close()
            self.add_dir(self.tempDir)
        # Remove temp dir
        if self.debug: print("Removing temp dir " + self.tempDir)
        shutil.rmtree(self.tempDir)
        self.tempDir = None                      
            
# Rudimentary tests
if 0:
    b = Zipblob()
    b.add_file("zipblob.html", "index.html", "w")
    b.check_out()
    print("Check temp dir. ",)
    os.system("pause")
    #b.check_in()
    print("Done!")
            
if 0:                        
    print("o-> Program started... ")
    b = Zipblob()
    b.add_file("work/singular-test.txt", "sub/test.txt")
    b.add_file("work/singular-test.txt", "sub/test.txt", "w") # replace with new!
    
    b.add_dir("work/testsub")
    b.add_dir("work/testsub")
    
    b.check_out()
    
    c = Zipblob()
    c.write(b.read())
    print("Check temp dir. ",)
    os.system("pause")
    
    b.check_in()
    
    # Export for trying out...
    f = open("work/out.zip","wb")
    f.write(b.read())
    f.close()
    #print b.getAsZIpFile()
    print("Done! ->(o)")
