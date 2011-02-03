#!/usr/bin/env python

try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
except:
    from distutils.core import setup

import sys
sys.path.append('matanui')
import matanui


setup(
    name = 'matanui',
    version = matanui.__version__,
    author = 'Guy K. Kloss',
    author_email = 'guy.kloss@aut.ac.nz',
    url = 'https://launchpad.net/matanui/',
    download_url = 'https://launchpad.net/matanui/+download',
    description = 'MataNui Replicating Grid Data Server',
    long_description = matanui.__doc__,
    packages = ['matanui'],
    provides = ['matanui'],
    keywords = 'dataserver mongodb rest restful json webservice gridfs grid distributed',
    license = 'Lesser General Public License v3',
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Environment :: Web Environment',
                   'Topic :: Internet',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Topic :: System :: Distributed Computing',
                   'Topic :: System :: Filesystems',
                   'Topic :: System :: Archiving',
                   ],
    required = ['pymongo'],
)
