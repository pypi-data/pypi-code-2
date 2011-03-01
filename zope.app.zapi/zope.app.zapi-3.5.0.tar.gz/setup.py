##############################################################################
#
# Copyright (c) 2006,2007 Zope Foundation and Contributors.
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
"""Setup for zope.app.zapi package"""

import os

from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    read('src', 'zope', 'app', 'zapi', 'README.txt')
    + '\n' +
    'Download\n'
    '========'
    )

setup(
    name='zope.app.zapi',
    version='3.5.0',
    url='http://pypi.python.org/pypi/zope.app.zapi',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Framework :: Zope3',
        ],
    description='Zope application programming interface',
    long_description=long_description,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope', 'zope.app'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'zope.app.interface',
        'zope.app.publisher',
        'zope.component >= 3.6',
        'zope.deprecation',
        'zope.interface',
        'zope.traversing',
        ],
    extras_require=dict(test=['zope.app.testing']),
    zip_safe=False,
    )
