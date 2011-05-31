from setuptools import setup

import os, os.path
import shutil

if not os.path.exists("scripts"):
    os.makedirs("scripts")
shutil.copyfile("runner.py", "scripts/omnikey2ivy")

#download and patch library
import omnikey2ivy.RFIDIOt

#read README file
long_desc=""
for fname in ['README.txt','INSTALL']:
    long_desc += "\n"*2+"-"*20+fname+"-"*20+"\n"*2
    with open(fname,'r') as f:
        long_desc+=f.read()

setup(
    name="omnikey2ivy",
    version="0.1.2",
    packages=["omnikey2ivy", "omnikey2ivy.RFIDIOt"],
    scripts=["scripts/omnikey2ivy"],
#setuptools stuffs
    install_requires = ['ivy-python>=2.1'],

#PyPi meta-data
    author="Fabien Andre",
    author_email="fabien.andre@enac.fr",
    description="emit card id on Ivy software bus",
    long_description=long_desc,
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        ],
    url="http://pypi.python.org/pypi/omnikey2ivy/",
)
