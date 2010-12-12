##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup for z3c.viewtemplate package

$Id: setup.py 118836 2010-12-12 16:20:00Z icemac $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.viewtemplate',
      version='0.4.1',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='View Templates',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Dcoumentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'z3c', 'viewtemplate', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 view template pagetemplate macro",
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
      url='http://cheeseshop.python.org/pypi/z3c.viewtemplate',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require = dict(
          test=['zope.app.testing',
                'zope.testing',
                ]),
      install_requires=[
          'setuptools',
          'zope.app.pagetemplate',
          'zope.component',
          'zope.configuration',
          'zope.contentprovider',
          'zope.i18nmessageid',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.tal',
          ],
      include_package_data = True,
      zip_safe = False,
      )
