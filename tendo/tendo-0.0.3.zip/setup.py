# chardet's setup.py
from distutils.core import setup
setup(
    name = "tendo",
    packages = ["tendo"],
    version = "0.0.3",
    description = "Python stdlib extensions, patches and improvements.",
    author = "Sorin Sbarnea",
    author_email = "sorin.sbarnea+tendo@gmail.com",
    url = "http://github.com/ssbarnea/tendo",
    download_url = "http://github.com/ssbarnea/tendo/archives/master",
    keywords = ["extension", "i18n", "stdlib", 'unicode'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3",
		"Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
		"License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: System :: Logging",
		"Topic :: Text Processing"
        ],
    long_description = """\
Tendo - Python stdlib extensions
-------------------------------------

colorer.py
 - enables coloring for console logging using Python logging module
 - tested on Windows, Linux and OS X
execfile2.py
 - extends execfile() by simulating Python execution from command line
 - enable you to call other python scripts with the same interpretor
tee.py
 - replacement for os.system() and subprocess.Popen()
 - add tee() implementation in Python
 - customizable logging
unicode.py
 - Unicode aware replacement for open()
 - recognizes byte order masks (BOM)
 - works with read mode and append mode
                                       
This version requires Python 2.6 or later. Works with Python 3.
"""
)