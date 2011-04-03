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
"""Setup

$Id: setup.py 121242 2011-04-03 20:17:56Z janjaapdriessen $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text + '\n\n'

setup(
    name = 'z3c.schema',
    version='0.7.2',
    author = 'Zope Community',
      author_email = "zope-dev@zope.org",
      description = "Additional schema fields for Zope 3",
    long_description=(
        read('README.txt') +
        '.. contents::\n\n'+
        read('CHANGES.txt') +
        read('src', 'z3c', 'schema', 'baseurl', 'README.txt') +
        read('src', 'z3c', 'schema', 'dateselect', 'README.txt') +
        read('src', 'z3c', 'schema', 'email', 'README.txt') +
        read('src', 'z3c', 'schema', 'hostname', 'README.txt') +
        read('src', 'z3c', 'schema', 'ip', 'README.txt') +
        read('src', 'z3c', 'schema', 'optchoice', 'README.txt') +
        read('src', 'z3c', 'schema', 'payments', 'README.txt') +
        read('src', 'z3c', 'schema', 'regex', 'README.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope zope3 z3c schema',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/z3c.schema',
    packages = find_packages('src'),
    include_package_data=True,
    package_dir = {'':'src'},
    namespace_packages=['z3c',],
    extras_require = dict(
      test=[
          'zope.testing',
           ]
    ),
    install_requires = [
      'setuptools',
      'zope.i18nmessageid',
      'zope.interface',
      'zope.schema >= 3.6',
      ],
    zip_safe=False,
)
