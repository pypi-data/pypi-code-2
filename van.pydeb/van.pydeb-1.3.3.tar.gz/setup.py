##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
from setuptools import setup, find_packages

long_description = open('README.txt', 'r').read()
long_description += '\n'
long_description += open('CHANGES.txt', 'r').read()

setup(name="van.pydeb",
      description='Make egg metadata information available for Debian packaging',
      long_description=long_description,
      author="Vanguardistas",
      url='http://pypi.python.org/pypi/van.pydeb',
      version='1.3.3',
      license = 'ZPL 2.1',
      packages=find_packages(),
      entry_points = {'console_scripts': ['van-pydeb = van.pydeb:main',]},
      namespace_packages=["van"],
      install_requires=[
          'setuptools',
          ],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Topic :: System :: Archiving :: Packaging',
                   'License :: DFSG approved',
                   'License :: OSI Approved :: Zope Public License',
                   'Framework :: Setuptools Plugin',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   ],
      include_package_data = True,
      zip_safe = False,
      )
