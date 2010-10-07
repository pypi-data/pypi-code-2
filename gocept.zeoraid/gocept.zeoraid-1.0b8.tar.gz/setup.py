##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
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
"""Setup for gocept.zeoraid package.
"""

from setuptools import setup, find_packages

name = "gocept.zeoraid"
setup(
    name=name,
    version='1.0b8',
    author="Zope Foundation and Contributors",
    author_email="ct@gocept.com",
    description="A ZODB storage for replication using RAID techniques.",
    long_description=open('README.txt').read(),
    license="ZPL 2.1",
    keywords="zodb buildout",
    classifiers=["Framework :: Buildout"],
    url='http://pypi.python.org/pypi/gocept.zeoraid',
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['gocept'],
    install_requires=[
        'mock',
        'setuptools',
        'zc.zodbrecipes',
        'ZODB3>=3.9dev',
        ],
    entry_points="""
        [zc.buildout]
        server = gocept.zeoraid.scripts.recipe:ZEORAIDServer

        [console_scripts]
        zeoraid = gocept.zeoraid.scripts.controller:main
        """)
