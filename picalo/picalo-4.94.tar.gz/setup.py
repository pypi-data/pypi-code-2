#!/usr/bin/env python
####################################################################################
#
# INSTRUCTIONS:
#
# To install Picalo system-wide (available to all Python programs),
# simply run:
#
#     python setup.py install
#
# from this directory.
#
#
####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
#                                                                                  #
# This file is part of Picalo.                                                     #
#                                                                                  #
# Picalo is free software; you can redistribute it and/or modify                   #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# Picalo is distributed in the hope that it will be useful,                        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################


#from distutils.core import setup
from setuptools import setup
import glob, sys, fnmatch, os, os.path, shutil

# returns a list of all the files in a directory tree
def walk_dir(dirname, mask=''):
  files = []
  ret = [ (dirname, files) ]
  for name in os.listdir(dirname):
    fullname = os.path.join(dirname, name)
    if os.path.isdir(fullname):
      ret.extend(walk_dir(fullname))
    elif not mask:
      files.append(fullname)
    elif fnmatch.fnmatch(name, mask):
      files.append(fullname)
  return ret

# this manifest enables the standard Windows-looking theme
manifest = ''' 
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" 
manifestVersion="1.0"> 
  <assemblyIdentity 
    version="0.6.8.0" 
    processorArchitecture="x86" 
    name="MyCare Card Browser" 
    type="win32" 
  /> 
  <description>MyCare Card Browser Program</description> 
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3"> 
    <security> 
      <requestedPrivileges> 
        <requestedExecutionLevel 
          level="asInvoker" 
          uiAccess="false" 
        /> 
      </requestedPrivileges> 
    </security> 
  </trustInfo> 
  <dependency> 
    <dependentAssembly> 
      <assemblyIdentity 
        type="win32" 
        name="Microsoft.VC90.CRT" 
        version="9.0.21022.8" 
        processorArchitecture="x86" 
        publicKeyToken="1fc8b3b9a1e18e3b" 
      /> 
    </dependentAssembly> 
  </dependency> 
  <dependency> 
    <dependentAssembly> 
      <assemblyIdentity 
        type="win32" 
        name="Microsoft.Windows.Common-Controls" 
        version="6.0.0.0" 
        processorArchitecture="x86" 
        publicKeyToken="6595b64144ccf1df" 
        language="*" 
      /> 
    </dependentAssembly> 
  </dependency> 
</assembly> 
''' 

# get this version of Picalo
VERSION = open(os.path.join(os.path.dirname(__file__), 'picalo/VERSION.txt')).read().strip()

# The basic options for Picalo
options = {
  'name':             'picalo',
  'version':          VERSION,
  'description':      'A data analysis/structure library with tables, type-aware columns, records, and cells.',
  'long_description': open(os.path.join(os.path.dirname(__file__), 'picalo/README.txt')).read(),
  'author':           'Conan C. Albrecht',
  'author_email':     'conan@warp.byu.edu',
  'url':              'http://www.picalo.org/',
  'keywords':         'data log analysis spreadsheet database',  
  'license':          open(os.path.join(os.path.dirname(__file__), 'picalo/LICENSE.txt')).read(),
  'packages':         [ 
                        'picalo', 
                        'picalo.lib', 
                        'picalo.lib.pyExcelerator',
                      ],
  'install_requires': [
                         'ZODB3',
                         'zc.blist',
                         'chardet',
                      ],
  'classifiers':      [
                        "Development Status :: 4 - Beta",
                        'Environment :: Console',
                        'Intended Audience :: Developers',
                        'Intended Audience :: Science/Research',
                        'License :: OSI Approved :: GNU General Public License (GPL)',
                        'Operating System :: OS Independent',
                        'Topic :: Database',
                        'Topic :: Internet :: Log Analysis',
                        'Topic :: Office/Business :: Financial :: Spreadsheet',
                        'Topic :: Scientific/Engineering',
                        'Topic :: Text Processing',
                      ],                 
  'data_files':       [ 
                      ],
}

# add additional options if we're packging the GUI with it
if len(sys.argv) >= 2 and sys.argv[1] in ( 'py2exe', 'py2app' ):
  options['packages'].extend(
                       [
                         'picalo.gui',
                         'picalo.gui.wizards',
                       ] 
  )
  options['scripts'] = [
                         'Picalo.pyw',
                       ]
  options['package_data'] = {  
                        'picalo': [ 
                           'picalo',
                           'picalo/resources', 
                           'picalo/tools',
                           'picalo/tools/Detectlets',
                           'picalo/tools/Detectlets/BidRigging',
                           'picalo/tools/Detectlets/PhantomVendors',
                           'picalo/tools/Detectlets/SplitPurchases',
                         ] 
                       }
  options['data_files'].extend([ 
                            ('picalo/gui/wizards', glob.glob('picalo/gui/wizards/*')),
                            ('picalo/resources', glob.glob('picalo/resources/*')),
                            ('picalo/tools', glob.glob('picalo/tools/*.py')),
                            ('picalo', glob.glob('picalo/*.txt')),
                          ] + walk_dir('picalo/tools/Detectlets', '*.py')),
                      

                      
# windows specific
if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
  try:
    import py2exe
  except ImportError:
    print 'Could not import py2exe.   Windows exe could not be built.'
    sys.exit(0)
  # windows-specific options
  options['windows'] = [
    {
      'script':'Picalo.pyw',
      'icon_resources': [
        ( 1, 'picalo/resources/appicon-win.ico' ),
      ],
      'other_resources': [
        ( 24, 1, manifest ),
      ],
    },
  ]
  options['options'] = {
    'py2exe': { 
      'packages': [ 
        'picalo', 
        'picalo.lib', 
        'picalo.lib.pyExcelerator',
        'picalo.gui',
        'picalo.gui.wizards',
      ],
      'includes': 'psycopg2, MySQLdb, pyodbc, pgdb, cx_Oracle, sqlite3, chardet, email.iterators', # email.iterators is only because of a python 2.6 and py2exe bug (somehow they don't get into the archive automatically like everything else)
     }
  }
  options['data_files'].append(('.',              glob.glob('*.dll')))  # required dlls for libraries to run correctly
  options['data_files'].append(('.',              glob.glob('*.manifest')))  # required manifest for libraries to run correctly

# mac specific
if len(sys.argv) >= 2 and sys.argv[1] == 'py2app':
  try:
    import py2app
  except ImportError:
    print 'Could not import py2app.   Mac bundle could not be built.'
    sys.exit(0)
  # mac-specific options
  options['app'] = ['Picalo.pyw']
  options['options'] = {
    'py2app': {
      'argv_emulation': True,
      'iconfile': 'picalo/resources/appicon-mac.icns',
      'packages': [ 
        'picalo', 
        'picalo.lib', 
        'picalo.lib.pyExcelerator',
        'picalo.gui',
        'picalo.gui.wizards',
      ],
      'includes': 'psycopg2, MySQLdb, pgdb, sqlite3, chardet,email.iterators', # email.iterators is only because of a python 2.6 and py2exe bug (somehow they don't get into the archive automatically like everything else)
    }
  }


# run the setup
setup(**options)      
