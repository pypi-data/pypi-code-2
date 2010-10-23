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

$Id: setup.py 81198 2007-10-30 08:08:29Z icemac $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text + '\n\n'

readmeText = read('./src/z3c/securitytool/README.txt')

setup (
    name='z3c.securitytool',
    version='0.5.1',
    author = "Daniel Blackburn, Stephan Richter, Randy Crafton",
    author_email = "zope-dev@zope.org",
    url="http://pypi.python.org/pypi/z3c.securitytool",
    description = "A security audit tool and demo for Zope3 views",
    long_description=(
        '.. contents::\n\n' +
        read('README.txt') +
        read('src', 'z3c', 'securitytool', 'README.txt')+
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 securitytool security",
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
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        demo = ['zope.app.securitypolicy',
                             'zope.app.session',
                             'zope.app.twisted',
                             'zope.app.zcmlfiles'],
        test = [
            'zope.app.container',
            'zope.testing',
            'z3c.coverage',
            'z3c.template',
            'zope.app.i18n',
            'zope.dublincore >= 3.7',
            ],
        adding = ['zope.app.container'],
        ),
    install_requires = [
        'setuptools',
        'zope.publisher',
        'zope.component',
        'zope.interface',
        'zope.app.pagetemplate',
        'zope.pagetemplate',
        'zope.app.zapi',
        'zope.security',
        'zope.session',
        'zope.testing',
        'zope.app.testing',
        'zope.app.twisted',
        'zope.app.apidoc',
        'zope.securitypolicy',
        'zope.app.security',
        'zope.app.securitypolicy',
        'zope.annotation',
        'zope.app.authentication',
        'zope.app.folder',
        'zope.testbrowser',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.configuration',
        'zope.event',
        'zope.lifecycleevent',
        'zope.location',
        'zope.schema',
        'z3c.macro',
        'z3c.layer.minimal',
        'zope.viewlet',
        ],
    zip_safe = False,
    )
