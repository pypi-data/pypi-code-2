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
from sleipnir.testing import constants
from setuptools import setup, find_packages

AUTHOR, EMAIL = re.match(r'^(.*) <(.*)>$', constants.__author__).groups()

setup(
    name         = "Hello",
    version      = constants.__version__,
    url          = constants.__url__,
    classifiers  = constants.__classifiers__,
    author       = AUTHOR,
    author_email = EMAIL,
    license      = constants.__license__,
    description  = """Hello Plugin""",
    packages     = find_packages(exclude=['*.tests*']),
    entry_points = """
    [%s]
    test.hello.component = hello_plugin.hello_world:Hello
    test.hello.hello     = hello_plugin.hello_world:HelloWorld
    """ % constants.__entry_point__,
)
