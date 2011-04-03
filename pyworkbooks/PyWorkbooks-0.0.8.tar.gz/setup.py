#! /usr/bin/env python
# -*- coding: utf-8 -*-
# setup.py
import sys

if sys.platform == 'win32':
   if len(sys.argv) < 2:
      sys.argv.append('install') # pretty sure they want to install... 
   
from distutils.core import setup
import os

version = '0.0.8'

if sys.platform != 'win32':
   setup(name = 'PyWorkbooks',
         version = version,
         author = 'Garrett Berg',
         url = 'https://sourceforge.net/projects/pyworkbooks/',
         packages = ['PyWorkbooks'],
         classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2'
            ],

         data_files = [('/usr/share/doc/python-PyWorkbooks', ['PyWorkbooks Documentation.pdf']),
                        #(os.path.expanduser('~') + '/.gnumeric/1.10.8/plugins/' , ['plugins'])
                      ]
         )

else:
   setup(name = 'PyWorkbooks',
         version = version,
         author = 'Garrett Berg',
         url = 'https://sourceforge.net/projects/pyworkbooks/',
         packages = ['PyWorkbooks'],
         classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2'
            ],
         )
