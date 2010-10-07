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

$Id: setup.py 117323 2010-10-07 09:17:18Z janwijbrand $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages


def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text

setup(
    name = 'z3c.recipe.i18n',
    version='0.8.0',
    author = 'Roger Ineichen and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'Zope3 egg based i18n locales extration recipes',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        + '\n\n' +
        '**********************\n'
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'recipe', 'i18n', 'README.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope3 z3c i18n locales extraction recipe',
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
    url = 'http://pypi.python.org/pypi/z3c.recipe.i18n',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.recipe'],
    extras_require = dict(
        test = [
            'zope.testing',
            'zc.lockfile',
            'zope.app.publication',
            'zope.component',
            'zope.configuration',
            'zope.container',
            'zope.error',
            'zope.event',
            'zope.interface',
            'zope.location',
            'zope.processlifetime',
            'zope.session',
            'zope.site',
            'zope.security',
            'zope.traversing',
            'ZODB3',
            ],
        ),
    install_requires = [
        'setuptools',
        'zc.buildout >= 1.5.1',
        'z3c.recipe.scripts >= 1.0.1',
        'zope.app.appsetup',
        'zope.app.locales[extract] >= 3.5.0',
        'zope.configuration',
        ],
    entry_points = {
        'zc.buildout': [
             'i18n = z3c.recipe.i18n.i18n:I18nSetup',
         ]
    },
)
