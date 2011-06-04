#!/usr/bin/env python
# Copyright (C) 2011 Canonical
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This file is part of dh_splitpackage.
#
# dh_splitpackage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation
#
# dh_splitpackage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dh_splitpackage.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

try:
    from setuptools import setup, find_packages
except ImportError:
    print("This package requires setuptools to be configured")
    print("It can be installed with debian/ubuntu package python-setuptools")
    raise


import dh_splitpackage


setup(
    name='dh_splitpackage',
    version="%d.%d.%d" % dh_splitpackage.__version__[0:3],
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@canonical.com",
    packages=find_packages(),
    url='https://launchpad.net/dh_splitpackage',
    test_suite='dh_splitpackage.test',
    description="dh_split - split monolithic installation directory into sub-packages without pulling your hair out",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
    ],
    entry_points="""
    [console_scripts]
    dh_splitpackage = dh_splitpackage.__main__:main
    """,
    data_files=[
        ("/usr/share/man/man1/", ["dh_splitpackage.1"]),
    ],
    install_requires=[
        'argparse',
        'simplejson',
    ],
)
