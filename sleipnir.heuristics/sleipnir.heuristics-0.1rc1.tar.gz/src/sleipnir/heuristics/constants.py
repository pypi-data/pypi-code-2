#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Heuristics constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.1rc1'
__date__             = '2011-01-04'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__modname__          = "heuristics"
__appname__          = __namespace__ + '.' + __modname__
__title__            = 'Sleipnir Heuristics'
__release__          = '1'
__summary__          = 'A logistic system'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2010, 2011 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development',
    ]

__long_description__ = """\
Add Here a a description to this package
"""

__requires__ = [
    __namespace__ + '.core >= 0.1rc1',
    'oset',
    ]
__tests_requires__ = [
    __namespace__ + '.components >= 0.1rc1',
    __namespace__ + '.testing    >= 0.1rc5',
    ]
