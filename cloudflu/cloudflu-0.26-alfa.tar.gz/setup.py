#!/usr/bin/env python

#--------------------------------------------------------------------------------------
## Copyright 2010 Alexey Petrov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""

#--------------------------------------------------------------------------------------
import sys, os, os.path

# To avoid using previoulsy cached contents for the distributed package
an_engine = sys.argv[ 0 ]
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )
a_manifest_file = os.path.join( an_engine_dir, 'MANIFEST' )
if os.path.isfile( a_manifest_file ) :
    os.remove( a_manifest_file )
    pass

an_engine = os.path.basename( an_engine )

# To generate list of automatically distributed scripts
a_scripts = []
for a_file in os.listdir( an_engine_dir ) :
    if a_file == an_engine :
        continue

    if os.path.isfile( a_file ) : 
        if os.access( a_file, os.X_OK ) :
            a_scripts.append( a_file )
            pass
        pass
    pass


#-------------------------------------------------------------------------------------
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import cloudflu

os.chdir( an_engine_dir ) # Run from the proper folder

setup( name = cloudflu.NAME,
       description = 'Delivers "Cloud Computing" commodities for OpenFOAM(R) users',
       long_description = """Sends user data in a cloud cluster, runs the appointed solver and feteches the output results back to the user""",
       author = 'Alexey Petrov',
       author_email = 'alexey.petrov.nnov@gmail.com', 
       license = 'Apache License, Version 2.0',
       url = 'http://sourceforge.net/projects/cloudflu',
       install_requires = [ 'boto >= 2.0b3', 'workerpool', 'paramiko', 'pexpect' ],
       platforms = [ 'linux' ],
       version = cloudflu.VERSION,
       classifiers = [ 'Development Status :: 3 - Alpha',
                       'Environment :: Console',
                       'Intended Audience :: Science/Research',
                       'License :: OSI Approved :: Apache Software License',
                       'Operating System :: POSIX',
                       'Programming Language :: Python',
                       'Topic :: Scientific/Engineering',
                       'Topic :: Utilities' ],
       packages = find_packages(),
       scripts = a_scripts,
       zip_safe = True )


#--------------------------------------------------------------------------------------

