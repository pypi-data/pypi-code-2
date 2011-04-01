#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Component constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.1rc1'
__date__             = '2010-10-10'
__license__          = 'Trac BSD License'

__namespace__        = "sleipnir"
__modname__          = "components"
__appname__          = __namespace__ + '.' + __modname__
__title__            = 'Sleipnir Components'
__release__          = '1'
__summary__          = 'A logistic system'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2010, 2011 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development',
    ]

__long_description__ = """\
Add Here a a description to this package
"""

from os import sep, pardir
from os.path import realpath, dirname, join

__plugin_dir__  = realpath(join(dirname(__file__), pardir, "plugins"))
__entry_point__ = __namespace__ + ".plugins"
