##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.securitypolicy package

$Id: setup.py 116807 2010-09-25 09:07:46Z icemac $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.securitypolicy',
    version='3.6.0',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description="ZMI-based management views for zope.securitypolicy",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords = "zope3 security policy",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/zope.app.securitypolicy',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['zope', 'zope.app'],
    extras_require = dict(
          test=[
              'zope.app.testing',
              'zope.app.zcmlfiles',
              'zope.login',
              'zope.publisher >= 3.12',
              'zope.testing >= 3.8',
              ]),
    install_requires=['setuptools',
                      'zope.annotation',
                      'zope.app.authentication',
                      'zope.app.form',
                      'zope.app.security',
                      'zope.browser',
                      'zope.component [hook]',
                      'zope.configuration',
                      'zope.exceptions',
                      'zope.i18n',
                      'zope.i18nmessageid >= 3.4.2',
                      'zope.interface',
                      'zope.location',
                      'zope.schema',
                      'zope.security',
                      'zope.securitypolicy',
                      ],
    include_package_data = True,
    zip_safe = False,
    )
