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

import os
import re
import sys

if sys.version_info < (2, 5):
    sys.stderr.write("Sleipnir requires Python 2.5 or higher.")
    sys.exit(0)

# Load constants
from sleipnir.components import constants
from setuptools import setup, find_packages

AUTHOR, EMAIL = re.match(r'^(.*) <(.*)>$', constants.__author__).groups()

setup(
    name         = "Fail",
    version      = constants.__version__,
    url          = constants.__url__,
    classifiers  = constants.__classifiers__,
    author       = AUTHOR,
    author_email = EMAIL,
    license      = constants.__license__,
    description  = """Fail Plugin""",
    package_dir  = {'fail':''},
    packages     = ['fail'],
    entry_points = """
    [%s]
    test.hello.fail  = fail
    """ % constants.__entry_point__,
)
