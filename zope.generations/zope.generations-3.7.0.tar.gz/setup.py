##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.generations package

$Id: setup.py 116566 2010-09-18 11:30:18Z icemac $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.generations',
      version='3.7.0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope application schema generations',
      long_description=(
          read('README.txt')
          + '\n\n.. contents::\n\n' +
          '======================\n'
          'Detailed Documentation\n'
          '======================\n'
          + '\n\n' +
          read('src', 'zope', 'generations', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope zodb schema generation",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.generations',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(test=[
          'ZODB3',
          'zope.app.publication',
          'zope.site',
          'zope.testing',
          ]),
      install_requires=[
          'setuptools',
          'transaction',
          'zope.component',
          'zope.interface',
          'zope.processlifetime',
          ],
      include_package_data = True,
      zip_safe = False,
      )
