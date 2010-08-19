##############################################################################
#
# Copyright (c) 2007-2009 Zope Foundation and Contributors.
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

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.10.0'

setup (
    name='z3c.profiler',
    version=version,
    author = "Stephan Richter, Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Profiler skin for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'profiler', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c profiler",
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
    url = 'http://pypi.python.org/pypi/z3c.profiler',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.etestbrowser',
            'zope.app.testing',
            ],
        app = [
            'zope.app.server',
            'zope.dublincore >= 3.7',
            ]
        ),
    install_requires = [
        'setuptools',
        'z3c.layer.pagelet',
        'z3c.macro',
        'z3c.pagelet',
        'z3c.template',
        'z3c.zrtresource',
        'zope.app.wsgi',
        'zope.browserpage',
        'zope.component >= 3.8.0',
        'zope.componentvocabulary',
        'zope.configuration >= 3.5.0',
        'zope.contentprovider',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.login',
        'zope.principalregistry',
        'zope.schema',
        'zope.security >= 3.6.0',
        'zope.securitypolicy',
        'zope.testing',
        'zope.traversing',
        'zope.viewlet',
        ],
    zip_safe = False,
)
