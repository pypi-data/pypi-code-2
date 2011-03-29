#!/usr/bin/env python
# -*- mode: Python; indent-tabs-mode: nil; coding: utf-8  -*-

#
# Copyright 2010, 2011 Carlos Martín
# Copyright 2010, 2011 Universidad de Salamanca
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""Main Setup File"""

import os
import re
import sys

if sys.version_info < (2, 5):
    sys.stderr.write("Sleipnir requires Python 2.5 or higher.")
    sys.exit(0)

# setuptools build required.
from setuptools import setup, find_packages, findall
from distutils.command.build import build as _build
from distutils.command.install_data import install_data as _install

# Load constants
sys.path.insert(0, 'src')
from sleipnir.testing import constants


def command_overrides(package):
    """
    Extend setuptools to create dinamically namespace __init__ stuff
    """

    SUBPKGS = [f.rpartition(os.sep)[0]                             \
        for f in findall('src' + os.sep + constants.__namespace__) \
        if f.endswith(os.sep + 'setup.py')]

    def _build_develop_plugin_eggs():
        """builds subpackages and adds an Egg link to parent dirs"""

        while True:
            FAILED, CURDIR = SUBPKGS[:], os.getcwd()
            for m in FAILED:
                os.chdir(m)
                argv = ['setup.py', 'develop', '-mxd', os.pardir + os.sep]
                if os.spawnvp(os.P_WAIT, 'python', ['python'] + argv) == 0:
                    SUBPKGS.remove(m)
                os.chdir(CURDIR)
            if FAILED == SUBPKGS:
                break
        if FAILED:
            for subpkg in FAILED:
                sys.stderr.write("Error in package %s\n" % subpkg)
            sys.exit(1)

    DATA = os.path.join('src', 'sleipnir', 'testing', 'data',)
    DESTDIR = os.path.join('share', 'sleipnir', 'testing',)

    def _install_extend_test_data(data_files, where):
        """Add subdirs into data_files"""

        def append_data_file(current, where):
            for _, dirs, files in os.walk(where):
                data_files.append(
                    (current,
                     [os.path.join(where, arch) for arch in files]))
                for children in dirs:
                    append_data_file(
                        os.path.join(current, children),
                        os.path.join(where, children))
                break

        SUBDIRS = ('interfaces', 'plugins', 'tsplib',)

        for subdir in SUBDIRS:
            append_data_file(
                os.path.join(DESTDIR, subdir),
                os.path.join(DATA, subdir))

    #pylint: disable-msg=R0904,C0103,C0111
    class build(_build):
        def run(self):
            _build_develop_plugin_eggs()
            _build.run(self)

    #pylint: disable-msg=R0904,C0103,C0111
    class install_data(_install):
        def run(self):
            _install_extend_test_data(self.data_files, DATA)
            _install.run(self)

    return dict(build=build, install_data=install_data)

# Test Data
DATA_ROOT_FILES = [
    (os.path.join('share', 'sleipnir', 'testing'),
     [os.path.join('src', 'sleipnir', 'testing', 'data', 'README')],
)]
# Peek author details
AUTHOR, EMAIL = re.match(r'^(.*) <(.*)>$', constants.__author__).groups()

setup(
    author             = AUTHOR,
    author_email       = EMAIL,
    classifiers        = constants.__classifiers__,
    description        = constants.__summary__,
    install_requires   = [],
    license            = constants.__license__,
    long_description   = constants.__long_description__,
    name               = constants.__appname__,
    namespace_packages = [constants.__namespace__],
    package_dir        = {'': 'src'},
    packages           = find_packages(where='src', exclude=['*interfaces']),
    url                = constants.__url__,
    version            = constants.__version__,
    zip_safe           = False,
    data_files         = DATA_ROOT_FILES,
    cmdclass           = command_overrides(constants.__appname__),
)
