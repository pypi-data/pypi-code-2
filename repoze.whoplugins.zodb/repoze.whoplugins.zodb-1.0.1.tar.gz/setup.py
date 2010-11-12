##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '1.0.1'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

requires = [
    'setuptools',
    'repoze.who',
    'repoze.zodbconn',
    'transaction',
    'ZODB3',
]

setup(name='repoze.whoplugins.zodb',
      version=__version__,
      description='ZODB authenticator and metadata plugin for repoze.who',
      long_description=README,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
      ],
      keywords='web application server wsgi zope zodb authentication',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze', 'repoze.who', 'repoze.who.plugins'],
      zip_safe=False,
      tests_require=requires,
      install_requires=requires,
      test_suite="repoze.who.plugins.zodb",
)
