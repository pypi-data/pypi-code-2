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
"""Setup

$Id: setup.py 82497 2007-12-28 14:59:22Z rogerineichen $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages


def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

setup(
    name = 'z3c.recipe.winservice',
    version='0.7.0',
    author = 'Roger Ineichen and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'Zope3 windows service installer',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope zope3 z3c deploy recipe windows service',
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
    url = 'http://pypi.python.org/pypi/z3c.recipe.winservice',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.recipe'],
    extras_require = dict(
        test = [
            'zope.testing',
            'zc.recipe.egg',
            'ZConfig >=2.4a5',
            ],
        ),
    install_requires = [
        'ZConfig >=2.4a5',
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],
    entry_points = {
        'zc.buildout': [
             'service = z3c.recipe.winservice.service:ServiceSetup',
         ]
    },
)
