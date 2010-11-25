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
## See http://sourceforge.net/apps/mediawiki/balloon-foam
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
ez_setup.use_setuptools( '0.6c9' )

from setuptools import setup, find_packages
import balloon

os.chdir( an_engine_dir ) # Run from the proper folder

setup( name = balloon.NAME,
       description = 'Set of cloud computing automation utilities',
       long_description = 
       """These utilities provide seemless mode for:
        - accessing to cloud;
        - deploying user specified data and functionality to be run on this data;
        - launching of the cloud specified task;
        - storing of output data into cloud;
        - fectching of these output results from cloud;
        - other miscellaneous functions""",
       author = 'Alexey Petrov',
       author_email = 'alexey.petrov.nnov@gmail.com', 
       license = 'Apache License, Version 2.0',
       url = 'http://sourceforge.net/projects/balloon-foam',
       install_requires = [ 'boto', 'workerpool', 'paramiko', 'pexpect' ],
       platforms = [ 'linux' ],
       version = balloon.VERSION,
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
       entry_points = { 'console_scripts': [
           'amazon_location_list.py = balloon.amazon.apps.location_list:main',
           'balloon-cluster-regions = balloon.amazon.apps.location_list:main',

           'amazon_reservation_run.py = balloon.amazon.apps.reservation_run:main',
           'balloon-reservation-run = balloon.amazon.apps.reservation_run:main',

           'amazon_reservation_list.py = balloon.amazon.apps.reservation_list:main',
           'balloon-cluster-ls = balloon.amazon.apps.reservation_list:main',

           'amazon_reservation_pickup.py = balloon.amazon.apps.reservation_pickup:main',

           'amazon_reservation_delete.py = balloon.amazon.apps.reservation_delete:main',
           'balloon-cluster-rm = balloon.amazon.apps.reservation_delete:main',

           'amazon_instance_extract.py = balloon.amazon.apps.instance_extract:main',
           'balloon-instance-extract = balloon.amazon.apps.instance_extract:main',

           'balloon_ssh.py = balloon.common.ssh.run:main',
           'balloon-ssh = balloon.common.ssh.run:main',

           'amazon_openmpi_config.py = balloon.amazon.apps.openmpi_config:main',
           'balloon-openmpi-config = balloon.amazon.apps.openmpi_config:main',

           'balloon-timestamps-upload = balloon.amazon.apps.timestamps_upload:main',

           'amazon_solver_run.py = balloon.amazon.apps.solver_run:main',
           'balloon-solver-run = balloon.amazon.apps.solver_run:main',

           'balloon-solver-start = balloon.amazon.apps.solver_start:main',
           'balloon-results-consume = balloon.amazon.apps.results_consume:main',

           'amazon_nfs_config.py = balloon.amazon.apps.nfs_config:main',
           'balloon-nfs-config = balloon.amazon.apps.nfs_config:main',

           'amazon_deploy_credentials.py = balloon.amazon.apps.deploy_credentials:main',
           'balloon-deploy-credentials = balloon.amazon.apps.deploy_credentials:main',

           'balloon_deploy.py = balloon.common.deploy:main',
           'balloon-deploy = balloon.common.deploy:main',

           'balloon-study-book = balloon.amazon.apps.study_book:main',
           'balloon-study-seal = balloon.amazon.apps.study_seal:main',

           'amazon_upload_start.py = balloon.amazon.apps.upload_start:main',
           'balloon-upload-start = balloon.amazon.apps.upload_start:main',

           'amazon_upload_resume.py = balloon.amazon.apps.upload_resume:main',
           'balloon-upload-resume = balloon.amazon.apps.upload_resume:main',

           'balloon-data-upload = balloon.amazon.apps.data_upload:main',

           'amazon_download.py = balloon.amazon.apps.download:main',
           'balloon-download = balloon.amazon.apps.download:main',

           'amazon_ls.py = balloon.amazon.apps.ls:main',
           'balloon-ls = balloon.amazon.apps.ls:main',

           'amazon_rm_study.py = balloon.amazon.apps.rm_study:main',
           'balloon-rm-study = balloon.amazon.apps.rm_study:main',

           'amazon_rm.py = balloon.amazon.apps.rm:main',
           'balloon-rm = balloon.amazon.apps.rm:main'
           ] },
       zip_safe = True )


#--------------------------------------------------------------------------------------

