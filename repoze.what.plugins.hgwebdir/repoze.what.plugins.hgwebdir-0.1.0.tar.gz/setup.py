# Copyright (c) 2010, Yaco Sistemas <lgs@yaco.es>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.

import os
from setuptools import setup, find_packages

from repoze.what.plugins.hgwebdir import version


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='repoze.what.plugins.hgwebdir',
    version=version,
    description='A simple repoze.what plugin useful for Mercurial hgwebdir',
    long_description='\n\n'.join([read('README.txt'), read('CHANGES.txt')]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
    keywords="authorization web application server wsgi repoze",
    author="Yaco Sistemas",
    author_email="lgs@yaco.es",
    namespace_packages=["repoze", "repoze.what", "repoze.what.plugins"],
    url="https://www.lorenzogil.com/projects/repoze.what.plugins.hgwebdir/",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'distribute',
        'repoze.what',
        ],
    )
