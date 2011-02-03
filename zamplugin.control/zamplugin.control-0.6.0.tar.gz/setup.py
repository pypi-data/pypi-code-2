###############################################################################
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
###############################################################################
"""Setup

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    data = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return data + '\n\n'

setup (
    name='zamplugin.control',
    version='0.6.0',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Error utility for Zope Application Management",
    long_description=(
        read('README.txt') +
        '.. contents::\n\n' +
        read('CHANGES.txt') +
        read('src', 'zamplugin', 'control', 'README.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 zam server and application control management",
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
    url = 'http://pypi.python.org/pypi/zamplugin.control',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zamplugin'],
    extras_require = dict(
        test = [
            'z3c.coverage',
            'z3c.testing',
            'zope.app.testing',
            'zope.app.zopeappgenerations', # needed by a test
            'zope.testbrowser',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.baseregistry',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.template',
        'zam.api >= 0.7',
        'zam.skin >= 0.8',
        'zope.app.generations',
        'zope.app.renderer',
        'zope.applicationcontrol',
        'zope.component',
        'zope.configuration >= 3.5',
        'zope.dublincore >= 3.7',
        'zope.interface',
        'zope.location',
        'zope.size',
        'zope.traversing',
        ],
    zip_safe = False,
)
