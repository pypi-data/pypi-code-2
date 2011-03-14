import urllib
import subprocess
import os
from sumatra.dependency_finder import find_xopened_files

local_filename = "bulbNet.zip"
if not os.path.exists(local_filename):
    urllib.urlretrieve("http://senselab.med.yale.edu/modeldb/eavBinDown.asp?o=2730&a=23&mime=application/zip", "bulbNet.zip")

if not (os.path.exists("bulbNet") and os.path.isdir("bulbNet")):
    subprocess.Popen("unzip bulbNet.zip", shell=True)
    
find_xopened_files("bulbNet/mosinit.hoc")
