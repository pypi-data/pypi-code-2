#!/usr/bin/env python

import sampy

from distutils.core import setup

from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name='sampy',
      py_modules=['sampy',],
      version=sampy.__release__, 
      url=sampy.__url__,
      author=sampy.__author__,
      author_email=sampy.__author_email__,
      description=sampy.__description__,
      long_description=sampy.__long_description__,
      platforms='All',
      license='GNU General Public License',
      classifiers=['Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Science/Research',
                   'Programming Language :: Python',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Software Development :: Libraries'
                   ],
      scripts=['sampy']
      )
