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
"""Setup for zope.app.authentication package

$Id: setup.py 117636 2010-10-18 09:50:37Z janwijbrand $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.authentication',
      version='3.9',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description=('Principals and groups management for '
                   'the pluggable authentication utility'),
      long_description=(
        read('README.txt')
        + '\n\n.. contents::\n\n' +
        read('src', 'zope', 'app', 'authentication', 'README.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'authentication', 'principalfolder.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'authentication', 'vocabulary.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
      url='http://pypi.python.org/pypi/zope.app.authentication',
      license='ZPL 2.1',
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
      keywords='zope3 authentication pluggable principal group',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      extras_require=dict(test=[
          'zope.app.testing',
          'zope.securitypolicy',
          'zope.app.zcmlfiles',
          'zope.securitypolicy',
          'zope.testbrowser',
          'zope.publisher',
          'zope.testing',
          'zope.session',
          'zope.formlib',
          'zope.publisher>=3.12',
          'zope.site',
          'zope.login',]),
      namespace_packages=['zope', 'zope.app'],
      install_requires=[
          'setuptools',
          'ZODB3',
          'zope.authentication',
          'zope.component',
          'zope.container',
          'zope.dublincore',
          'zope.event',
          'zope.exceptions',
          'zope.formlib >= 4.0.2',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.location',
          'zope.password >= 3.5.1',
          'zope.pluggableauth >= 1.1',
          'zope.schema',
          'zope.security',
          'zope.traversing',
          # Needed for browser code.
          'zope.app.container',
          'zope.app.component',
          ],
      include_package_data = True,
      zip_safe = False,
      )
