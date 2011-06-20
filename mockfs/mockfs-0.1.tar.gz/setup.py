#!/usr/bin/python
# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of mockfs.
#
# mockfs is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# mockfs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mockfs.  If not, see <http://www.gnu.org/licenses/>.

try:
    from setuptools import setup
except ImportError:
    print "This package requires setuptools to be configured"
    print "It can be installed with debian/ubuntu package python-setuptools"
    raise


try:
    import versiontools
except ImportError:
    print "This package requires python-versiontools to be configured"
    print "See: http://packages.python.org/versiontools/installation.html"
    raise


import mockfs


setup(
    name="mockfs",
    version=versiontools.format_version(mockfs.__version__),
    description=mockfs.__doc__.strip().splitlines()[0],
    author='Zygmunt Krynicki',
    author_email='zygmunt.krynicki@canonical.com',
    url='http://launchpad.net/mockfs',
    test_suite='test_mockfs',
    long_description=mockfs.__doc__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing",
    ],
    py_modules=["mockfs"],
    install_requires=["distribute"],
    setup_requires=["versiontools"],
    license="LGPL3",
    zip_safe=True,
)
