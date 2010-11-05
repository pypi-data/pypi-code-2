#!/usr/bin/env python

''' PyTTY - Python serial access package '''

__credits__ = '''Copyright (C) 2010 Arc Riley

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program; if not, see http://www.gnu.org/licenses
'''
__author__  = 'Arc Riley'
__version__ = '0.1'

import sys
from distutils.core import setup

setup(
  #
  #############################################################################
  #
  # PyPI settings (for pypi.python.org)
  #
  name             = 'PyTTY',                    # Name of project, not module
  version          = __version__.split()[0],     # Release version or "Trunk"
  description      = 'Python serial access package',
  long_description = ''' ''',                              
  maintainer       = 'Arc Riley',
  maintainer_email = 'arcriley@gmail.org',
  download_url     = 'http://hg.concordance-xmpp.org/pytty',
  license          = 'GNU Lesser General Public License version 3 (LGPLv3)',
  classifiers      = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Topic :: Communications',
    'Topic :: Terminals :: Serial',
  ],
  #
  #############################################################################
  #
  # Package settings
  #
  packages         = ['pytty',
  ],
  package_dir      = {'pytty' : 'src',
  },
  #
  #############################################################################
)
