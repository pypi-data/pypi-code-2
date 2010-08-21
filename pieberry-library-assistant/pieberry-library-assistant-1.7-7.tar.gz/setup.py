from distutils.core import setup
import os
from pprint import pprint

ics = [os.path.join('pieberry', i) for i in os.listdir('pieberry') if os.path.splitext(i)[1] == '.png']

try:
    import py2exe
    imfiles = ('.', ics)
    # origIsSystemDLL = py2exe.build_exe.isSystemDLL
    # def isSystemDLL(pathname):
    #     if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll"):
    #         return 0
    #     return origIsSystemDLL(pathname)
    # py2exe.build_exe.isSystemDLL = isSystemDLL
except:
    imfiles = ('pieberry', ics)

files=[
    ('.', ['pieberry.ico', 'pieberry32.ico']), 
    imfiles, 
    ('pieberry', ['pieberry/help/manual.html', 'pieberry/help/pieberrymanual.hhp', 'pieberry/help/pieberrymanual_contents.hhc', 'pieberry/help/pieberrymanual_index.hhk'])
    ]

#manifest for py2exe
manifest = """
 <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
 <assembly xmlns="urn:schemas-microsoft-com:asm.v1"
 manifestVersion="1.0">
 <assemblyIdentity
     version="0.64.1.0"
     processorArchitecture="x86" 
     name="Controls"
     type="win32"
 />
 <description>Your Application</description>
 <dependency>
     <dependentAssembly>
         <assemblyIdentity
             type="win32"
             name="Microsoft.Windows.Common-Controls"
             version="6.0.0.0"
             processorArchitecture="X86"
             publicKeyToken="6595b64144ccf1df"
             language="*"
         />
     </dependentAssembly>
 </dependency>
 </assembly>
 """

classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications :: GTK',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Programming Language :: Python :: 2.5',
    'Topic :: Text Processing :: Markup :: LaTeX',
    'Operating System :: OS Independent'
    ]


opts = {
    "py2exe": {
        "includes": "BeautifulSoup, pyPdf, pybtex, hachoir_metadata",
#        "dll_excludes": ["MSVCP90.dll"]
        }
    }

setup(name = "pieberry-library-assistant",
      version = "1.7-7",
      description = "A program to download pdf documents from public websites, and catalogue them in BibTeX format",
      author = "Raif Sarcich",
      author_email = "raifsarcich@gmail.com",
      url = "http://members.iinet.net.au/~raifsarcich/pieberry/",
      download_url = 'http://members.iinet.net.au/~raifsarcich/pieberry/',
      classifiers = classifiers,
      license = 'GNU General public licence',
      #Name the folder where your packages live:
          #(If you have other packages (dirs) or modules (py files) then
      #put them into the package directory - they will be found 
      #recursively.)
      packages = ['pieberry', 'atomise', 'pieberry.utility'],
      #'package' package must contain files (see list above)
      #I called the package 'package' thus cleverly confusing the whole issue...
      #This dict maps the package name =to=> directories
      #It says, package *needs* these files.
      package_data = {'pieberry' : ['*.png'],
                      'pieberry': ['help/*.html', 'help/*.hhp', 'help/*.hhc', 'help/*.hhk']},
      install_requires = ['pyPdf', 'BeautifulSoup', 'pybtex', 'hachoir_metadata'],
      # data_files = [("pieberry", "pieberry/*.png"), (".", "*.png")],
      #'runner' is in the root.
      scripts = ["pieberrydm", 'pieberrydm.pyw'],
      long_description = """PIEBERRY (IT'S FOR YOUR LIBRARY)

This is a program which I wrote to automate a painful aspect of my
work-life - downloading, storing, cataloguing and referencing
documents from (mainly public sector & government) websites.

These websites publish reams of documents in pdf format, usually in a
random range of cryptic CMS-generated filename schemas, with
incomplete or non-existent file metadata. 

Typically I download these, rename them with an intelligible title, a
six-digit archival date prefix, store then in an appropriate folder,
and enter them into my database of reference materials for use with
LaTeX/BibTex.

Actually, scratch that. What I REALLY do is download them, leave them
on my Desktop folder, look at them once, forget them, fill up my disk
quota, delete them, realise I've lost them and download them all over
again.

Hence, Pieberry, which will do all of the good and none of the bad
described above.

It's mainly for my use, but I hope that someone else will find it
useful. I'm open to requests for features.

It's written in Python, with the PortablePython 2.5.4 distribution
(which contains wxpython) in mind, but also requires Beautiful Soup,
pyPdf and Pybtex, which are all available through easy_install from
setuptools.""",
      windows = [{
            "script": 'pieberrydm.pyw',
            #"console": 'pieberrydm.pyw',
            "icon_resources": [(0, 'pieberry.ico')],
            "other_resources": [(24, 1, manifest)]
            }],
      data_files=files,#[('.', ['pieberry.ico', 'pieberry32.ico']),('pieberry',ics)],
      options = opts
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
) 
