#!/usr/bin/env python
import sys
from distutils.core import setup

try:
   from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
   from distutils.command.build_py import build_py

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: Microsoft :: Windows',
               'Operating System :: Unix',
               'License :: OSI Approved :: MIT License',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Printing']

long_description = open('README').read()

if sys.platform.lower().startswith('win'):
    requires = ['win32print']
else:
    requires = []

setup(name             = 'zebra',
      version          = '0.0.1a',
      py_modules       = ['zebra'],
      author           = 'Ben Croston',
      author_email     = 'ben@croston.org',
      maintainer       = 'Ben Croston',
      maintainer_email = 'ben@croston.org',
#      url              = 'http://www.wyre-it.co.uk/zebra/',
      description      = 'A package to communicate with (Zebra) label printers using EPL2',
      long_description = long_description,
      platforms        = 'Windows, Unix',
      classifiers      = classifiers,
      license          = 'MIT',
      cmdclass         = {'build_py': build_py},
      requires         = requires,
      )

