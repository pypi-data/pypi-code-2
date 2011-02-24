#!/usr/bin/env python
#
# Provide distutils setup.py
#
from distutils.core import setup
import sys
import os
import fnmatch
sys.path.append('./src')
from provide import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))

# todo: package description.

def getDataFiles(dest, basePath, pathOffset, glob = '*.*'):
    """
    Get all files matching glob from under pathOffset put give their pathes
    relative to basePath
    """
    result = []
    pathToWalk = os.path.join(basePath, pathOffset)
    for root, dirs, files in os.walk(pathToWalk):
        if not '.svn' in root:
            toffset = root[len(basePath)+1:]
            toffsetForDest = root[len(pathToWalk)+1:]
            tfileNames = fnmatch.filter(files, glob)
            fileList = [os.path.join(toffset, fname) for fname in tfileNames]
            tdest = os.path.join(dest, toffsetForDest)
            result.append( (tdest, fileList) )
    return result

def getPackages(basePath):
    result = []
    for root, dirs, files in os.walk(basePath):
        if not '.svn' in root and '__init__.py' in files:
            toffset = root[len(basePath)+1:]
            result.append( toffset )
    return result

def getScripts(basePath, offset):
    """
    Assumes all scripts are in base directory
    """
    scriptsList = []
    scriptsDir = os.path.join(basePath, offset)
    for fileName in os.listdir(scriptsDir):
        if not ('.svn' in fileName or '.bak' in fileName):
            scriptsList.append(os.path.join(offset, fileName))
    return scriptsList

setup(
    name='provide',
    version=__version__,
    author='Appropriate Software Foundation',
    author_email='provide-dev@appropriatesoftware.net',
    license='GPL',
    url='http://appropriatesoftware.net/provide/Home.html',
    download_url='http://appropriatesoftware.net/provide/docs/provide-%s.tar.gz' % __version__,
    description='Provide is a domainmodel application which supports application service provision work.',
    long_description =\
"""
Provide supports providing software applications as services, and migrating production services safely and seamlessly through an indefinite series of software application releases.

The purpose of the product and the scope of the supported work are described on this page:
http://appropriatesoftware.net/provide/Features.html

A tutorial in usage of the provide system here:
http://appropriatesoftware.net/provide/Documentation.html

""",
    
    package_dir={'': 'src'},
    packages=getPackages(os.path.join(basePath, 'src')),
    scripts=['bin/provide', 'bin/provide-makeconfig'],
    data_files=[
        ('var/log', []),
        ('var/www', [])
    ] + getDataFiles('vendor', basePath, 'vendor'),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    zip_safe=False, 
)

