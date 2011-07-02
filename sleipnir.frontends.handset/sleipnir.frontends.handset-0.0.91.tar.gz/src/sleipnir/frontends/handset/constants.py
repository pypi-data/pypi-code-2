#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Handset frontend constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.0.91'
__date__             = '2011-15-04'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__family__           = "frontends"
__modname__          = "handset"
__appname__          = __namespace__ + '.' + __family__ + '.' + __modname__
__title__            = 'Sleipnir N900 UX'
__release__          = '1'
__summary__          = 'UX experience for Nokia N900 (Handset) and Meego'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2011 Carlos Martín'

__gettext__    = __namespace__.lower()

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    "Environment :: Handhelds/PDA's",
    "Intended Audience :: Customer Service",
    "Operating System :: POSIX :: Linux",
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    "Topic :: Office/Business :: Scheduling",
    ]

__long_description__ = """\
Add Here a a description to this package
"""

__requires__ = [
    __namespace__ + '.core       >= 0.1.90',
    __namespace__ + '.components >= 0.1.90',
    __namespace__ + '.shell      >= 0.0.93',
    ]
__tests_requires__ = [
    __namespace__ + '.core       >= 0.1.90',
    __namespace__ + '.components >= 0.1.90',
    __namespace__ + '.shell      >= 0.0.93',
    __namespace__ + '.testing    >= 0.1rc6',
    ]

try:
    import os
    import sys
    from sleipnir.core.decorators import cached
except ImportError:
    def cached(func):
        """Just return cached method"""
        return func


@cached
def get_basedir():
    """Get base dir for package or prefix"""
    prefix = os.path.dirname(__file__)
    prefix = os.path.normpath(os.path.join(prefix, (os.pardir + os.sep) * 4))
    return sys.prefix if prefix.startswith(sys.prefix) else prefix


@cached
def get_datadir():
    """Get data dir"""
    prefix = get_basedir()
    share = os.path.join('share', __appname__)
    share = share if prefix.startswith(sys.prefix) else 'data'
    return os.path.join(prefix, share)


# pylint: disable-msg=E1101
# Common directories
__ui_dir__ = os.path.join(get_datadir(), 'ui')
__views_dir__ = os.path.join(os.path.dirname(__file__), 'views')
__entry_point__ = __namespace__ + '.' + __family__


#pylint: disable-msg=C0103
def QML(filename, target):
    """QML locator helper"""
    qmlfile = os.path.splitext(os.path.basename(filename))[0] + '.qml'
    for custom in (target, 'common'):
        qmlpath = os.path.join(__ui_dir__, 'qml', custom, qmlfile)
        if os.path.exists(qmlpath):
            return qmlpath
    raise LookupError("QML resource at '%s' not found", qmlpath)
