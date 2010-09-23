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

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.jsontree',
    version='0.6.0',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "JSON RPC item tree for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'jsontree', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c json rpc tree",
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
    url = 'http://pypi.python.org/pypi/z3c.jsontree',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.testing',
            'zope.app.component',
            'zope.app.publication',
            'zope.app.testing',
            'zope.browsermenu',
            'zope.browserpage',
            'zope.browserresource',
            'zope.configuration',
            'zope.pagetemplate',
            'zope.principalregistry',
            'zope.security',
            'zope.site',
            'zope.testing',
            'zope.testbrowser',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.json',
        'z3c.jsonrpc',
        'z3c.jsonrpcproxy',
        'z3c.template',
        'z3c.xmlhttp',
        'zope.component',
        'zope.container',
        'zope.contentprovider',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.proxy',
        'zope.publisher',
        'zope.security',
        'zope.traversing',
        'zope.viewlet',
        ],
    zip_safe = False,
)
