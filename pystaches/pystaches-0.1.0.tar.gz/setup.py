#!/usr/bin/env python

import sys, os
from distutils.core import setup

version = '0.1.0'
setup(
   name =          'pystaches',
   version =       version,
   description =   'Pystache extensions',
   author =        'Jonhnny Weslley',
   author_email =  'jw [at] jonhnnyweslley.net',
   url =           'http://github.com/jweslley/pystaches',
   download_url =  'http://github.com/jweslley/pystaches/tarball/v%s' % version,
   packages =      ['pystaches'],
   license =       'MIT',
   requires =      ["pystache", "pygments"],
   classifiers =   ['Development Status :: 4 - Beta',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2.5',
                    'Programming Language :: Python :: 2.6'
                   ]
)
