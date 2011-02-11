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
"""Setup for z3c.blobfile package

$Id: setup.py 120287 2011-02-11 18:30:21Z ldr $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.blobfile',
      version='0.1.5',
      author = "Zope Community",
      author_email = "zope-dev@zope.org",
      license = "ZPL 2.1",
      keywords = "zope3 ZODB blob file image content",
      url='http://pypi.python.org/pypi/z3c.blobfile',
      description='File and Image Using Blob Support of ZODB -- Zope 3 Content Components',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '----------------------\n'
          + '\n\n' +
          read('src', 'z3c', 'blobfile', 'blobfile.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      
      namespace_packages=['z3c'],
      
      extras_require = dict(test=['zope.app.file',
                                  'zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.testbrowser']),
      install_requires=['setuptools',
                        'ZODB3',
                        'zope.app.publication',
                        'zope.contenttype',
                        'zope.datetime',
                        'zope.dublincore',
                        'zope.event',
                        'zope.exceptions',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.publisher',
                        'zope.schema',
                        'zope.size',
                        'zope.app.file',
                        'zope.copy',
                        
                        ],
      include_package_data = True,
      zip_safe = False,
      )

