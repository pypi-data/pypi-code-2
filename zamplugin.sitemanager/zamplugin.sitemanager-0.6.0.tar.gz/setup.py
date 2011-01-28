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

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='zamplugin.sitemanager',
    version='0.6.0',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Site manager support for ZAM (Zope Application Management)",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 site manager application management user interface",
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
    url = 'http://pypi.python.org/pypi/zamplugin.sitemanager',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zamplugin'],
    extras_require = dict(
        test = [
            'z3c.coverage',
            'z3c.testing',
            'zope.app.appsetup',
            'zope.app.authentication',
            'zope.app.component',
            'zope.app.keyreference',
            'zope.app.publication',
            'zope.app.schema',
            'zope.app.testing',
            'zope.copypastemove',
            'zope.i18n',
            'zope.publisher',
            'zope.schema',
            'zope.security',
            'zope.securitypolicy',
            'zope.session',
            'zope.testing',
            'zope.testbrowser',
            'zope.app.principalannotation',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.baseregistry',
        'z3c.batching',
        'z3c.batching',
        'z3c.contents',
        'z3c.form >= 2.1',
        'z3c.formui >= 2.1',
        'z3c.json',
        'z3c.jsonrpc',
        'z3c.jsontree',
        'z3c.jsonrpcproxy',
        'z3c.layer.pagelet',
        'z3c.layer.ready2go',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.table',
        'z3c.xmlhttp',
        'z3c.zrtresource',
        'zam.api >= 0.7',
        'zope.app.component',
        'zope.app.http',
        'zope.app.intid',
        'zope.app.publisher',
        'zope.app.securitypolicy',
        'zope.app.server',
        'zope.app.twisted',
        'zope.configuration',
        'zope.interface',
        'zope.publisher',
        'zope.traversing',
        'zope.viewlet',
        ],
    zip_safe = False,
)
