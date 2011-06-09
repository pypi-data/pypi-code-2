#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Handset frontend constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.0.90'
__date__             = '2011-15-04'
__license__          = 'All rights reserved'

__namespace__        = "sleipnir"
__family__           = "frontends"
__modname__          = "handset"
__appname__          = __namespace__ + '.' + __family__ + '.' + __modname__
__title__            = 'Sleipnir N900 UX'
__release__          = '1'
__summary__          = 'UX experience for Nokia N900 (Handset) and Meego'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2011 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
	'License :: Other/Proprietary License',
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

__requires__       = [
    __namespace__ + '.components >= 0.1.90',
    __namespace__ + '.core       >= 0.1.90',
    __namespace__ + '.shell      >= 0.0.93',
    ]
__tests_requires__ = [
    __namespace__ + '.components >= 0.1.90',
    __namespace__ + '.core       >= 0.1.90',
    __namespace__ + '.shell      >= 0.0.93',
    __namespace__ + '.testing    >= 0.1rc6',
    ]


try:
    from os import path
    from sleipnir.shell import constants
    from sleipnir.shell.constants import System as BaseSystem

    #pylint: disable-msg=E1101
    class System(BaseSystem):
        """Derived class to adjust prefix to frontend package"""

        def __init__(self):
            super(System, self).__init__(__file__, __modname__)

        def get_libdir(self):
            """Get python system libdir"""
            return path.join(self.get_srcdir(),  \
                __namespace__, __family__, self._modname)

        def get_viewdir(self):
            """Get views dir for handset"""
            return path.join(self.get_libdir(), 'views')

        # pylint: disable-msg=R0201
        def get_entry_point(self):
            """Get Sleipnir.Components defined Entry Point"""
            return constants.__entry_point__

    # pylint: disable-msg=E1101
    # Common directories
    __ui_dir__      = System.get_instance().get_uidir()
    __views_dir__   = System.get_instance().get_viewdir()
    __entry_point__ = System.get_instance().get_entry_point()

except ImportError:
    __ui_dir__ = __views_dir__ = None
    __entry_point__ = __namespace__ + ".frontends"


#pylint: disable-msg=C0103
def QML(filename, target):
    """QML locator helper"""
    qmlfile = path.splitext(path.basename(filename))[0] + '.qml'
    for custom in (target, 'common'):
        qmlpath = path.join(__ui_dir__, 'qml', custom, qmlfile)
        if path.exists(qmlpath):
            return qmlpath
    raise LookupError("QML resource at '%s' not found", qmlpath)
