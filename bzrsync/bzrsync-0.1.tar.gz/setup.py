#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Installation script for BzrSync

Run it with
 'python setup.py install', or
 'python setup.py --help' for more options

Copyright (C) 2011 Marco Pantaleoni. All rights reserved.

@author: Marco Pantaleoni
@copyright: Copyright (C) 2011 Marco Pantaleoni
"""

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2011 Marco Pantaleoni"
__license__   = "GNU GPL v2"

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages
import os, sys

from bzrsync.setup_info import VERSION
#from bzrsync.finddata import find_package_data

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = read('README.txt')

revno = os.popen('bzr revno').read().strip()
version = '%s' % VERSION
if version.endswith('dev'):
    version = '%s-BZR-r%s' % (version, revno)
pypi_version = version
pypi_version = pypi_version.replace('_', '-')
pypi_version = pypi_version.replace('@', '-')

setup(
    name = 'bzrsync',
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://pypi.python.org/pypi/bzrsync/',
    license = 'GNU GPL v2',
    description = 'Tool to automatically synchronize Bazaar repositories between multiple nodes',
    long_description = long_description,
    keywords = 'softwarefabrica bazaar bzr sync bzrsync synchronize synchronization repositories branches vcs version control',
    classifiers=[
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.6',
        'Environment :: Console',
        ],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    #namespace_packages=['bzrsync'],
    include_package_data=True,
    exclude_package_data = {
        '': ['.bzr'],
    },
    zip_safe=True,
    entry_points = {
        'console_scripts': [
            'bzrsync = bzrsync.cmd:main',
        ],
    },
    setup_requires=['setuptools',
                    ],
    install_requires=['automa>=0.1.19',
                      'CmdUtils',
                      'bzr',
                      'PyYAML>=3.09',
                      'simplejson>=2.1.2',
                      'jsonrpc2>=0.3',
                      # -*- Extra requirements: -*-
                      ],
)
