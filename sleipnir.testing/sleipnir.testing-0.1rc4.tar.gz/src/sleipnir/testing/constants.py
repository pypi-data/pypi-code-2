#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Component constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.1rc4'
__date__             = '2010-10-10'
__license__          = 'PSF2'

__namespace__        = "sleipnir"
__modname__          = "testing"
__appname__          = __namespace__ + '.' + __modname__
__title__            = 'Sleipnir Testing'
__release__          = '1'
__summary__          = 'Sleipnir Testing'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2010, 2011 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: Python Software Foundation License',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Software Development',
    ]

__long_description__ = """\
Add Here a a description to this package
"""

from os import sep, pardir
from os.path import realpath, dirname, join, exists
from sys import prefix


def __get_data_dir():
    """Gets Plugin dir for testing plugins"""

    datadir = realpath(join(dirname(__file__), "data"))
    if not exists(datadir):
        datadir = join(prefix, 'share', __namespace__, __modname__)
    return datadir

__entry_point__ = __namespace__ + ".plugins"

__data_dir__   = __get_data_dir()
__plugin_dir__ = join(__data_dir__, "plugins")
__iface_dir__  = join(__data_dir__, "interfaces")
__tsplib_dir__ = join(__data_dir__, "tsplib")
