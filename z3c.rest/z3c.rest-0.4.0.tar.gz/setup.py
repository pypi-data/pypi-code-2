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

$Id: setup.py 117233 2010-10-05 06:58:04Z icemac $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

chapters = '\n'.join(
    [read('src', 'z3c', 'rest', name)
    for name in ('README.txt',
                 'client.txt',
                 'null.txt',
                 'traverser.txt',
                 'rest.txt')])

setup (
    name='z3c.rest',
    version='0.4.0',
    author = "Stephan Richter and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "A REST Framework for Zope 3 Applications",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' + chapters
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 form widget",
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
    url = 'http://cheeseshop.python.org/pypi/z3c.rest',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        app = ['zope.app.appsetup',
               'zope.app.authentication',
               'zope.app.component',
               'zope.app.container',
               'zope.app.error',
               'zope.app.form',
               'zope.app.publisher',
               'zope.app.publication',
               'zope.app.security',
               'zope.app.securitypolicy',
               'zope.app.twisted',
               'zope.app.wsgi',
               'zope.app.zcmlfiles',
               'zope.contentprovider',
               ],
        test = [
            'z3c.coverage',
            'z3c.etestbrowser',
            'zope.app.container',
            'zope.app.testing',
            ],
        ),
    install_requires = [
        'lxml>=2.0.0', # Changes in API, since 1.3.6.
        'setuptools',
        'z3c.traverser>=0.2.2', # BasePluggableTraverser only available
                                # in 0.2.2 and higher
        'zope.publisher',
        'zope.app.http',
        ],
    zip_safe = False,
    )
