### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

"""
This module contains ztfy.blog package
"""
import os
from setuptools import setup, find_packages

DOCS = os.path.join(os.path.dirname(__file__),
                    'ztfy', 'blog', 'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.2.2'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.blog',
      version=version,
      description="ZTFY blog handling package",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='ZTFY Zope3 blog package',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://trac.ztfy.org/ztfy.blog',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.css', '*.js']},
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "ztfy.comment.tests.test_commentdocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pygments',
          'z3c.form',
          'z3c.formui',
          'z3c.formjs',
          'z3c.table',
          'z3c.menu.simple',
          'zope.app.zapi',
          'zopyx.txng3.core',
          'zopyx.txng3.ext',
          'ztfy.utils',
          'ztfy.workflow',
          'ztfy.i18n',
          'ztfy.extfile',
          'ztfy.file',
          'ztfy.skin',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
