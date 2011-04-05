#!/usr/bin/env python
# -*- mode: Python; indent-tabs-mode: nil; coding: utf-8  -*-

#
# Copyright 2010, 2011 Carlos Martín
# Copyright 2010, 2011 Universidad de Salamanca
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""Main Setup File """

from __future__ import absolute_import

import os
import re
import sys

if sys.version_info < (2, 5):
    sys.stderr.write("Sleipnir requires Python 2.5 or higher.")
    sys.exit(0)

# Load constants
sys.path.insert(0, (os.pardir + os.sep) * 7 + 'src')
from sleipnir.testing import constants

# setuptools build required.
from setuptools import setup, find_packages
from setuptools.command.develop import develop as _develop


def command_overrides():
    """
    Extend setuptools to create fix egg links
    """
    from itertools import ifilter

    def patch_egg(base=os.curdir, egg_name='.egg-link'):
        """Replace string"""

        def relpath(dest, base):
            """calculate relative path"""
            base = os.path.normpath(base).split(os.sep)
            dest = os.path.normpath(dest).split(os.sep)

            i = 0
            for i in xrange(min(1, len(dest)), min(len(base), len(dest))):
                if base[i] != dest[i]:
                    break
                i = i + 1
            return os.path.join(*([os.pardir] * (len(base) - i) + dest[i:]))

        for root, _, files in os.walk(base):
            for lnk in ifilter(lambda x: x.endswith(egg_name), files):
                with open(root + os.sep + lnk, 'rw+') as iof:
                    line = relpath(iof.readline(), base)
                    rest = iof.read()
                    iof.seek(0)
                    iof.truncate()
                    iof.write(line + rest)

    #pylint: disable-msg=R0904,C0103,C0111
    class develop(_develop):
        def run(self):
            _develop.run(self)
            base = os.path.abspath(os.path.dirname(__file__))
            patch_egg(self.install_dir, os.path.basename(base) + '.egg-link')

    return dict(develop=develop)

# Peek author details
AUTHOR, EMAIL = re.match(r'^(.*) <(.*)>$', constants.__author__).groups()

setup(
    name         = "sleipnir.testing.plugins.fail",
    version      = constants.__version__,
    url          = constants.__url__,
    classifiers  = constants.__classifiers__,
    author       = AUTHOR,
    author_email = EMAIL,
    license      = constants.__license__,
    description  = """Fail Testing Plugin""",
    package_dir  = {'fail':''},
    packages     = ['fail'],
    cmdclass     = command_overrides(),
    entry_points = """
    [%s]
    test.hello.fail  = fail
    """ % constants.__entry_point__,
)
