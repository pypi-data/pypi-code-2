#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Shell constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.0.90'
__date__             = '2010-10-10'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__modname__          = "shell"
__appname__          = __namespace__ + '.' + __modname__
__title__            = 'Sleipnir Shell'
__release__          = '1'
__summary__          = 'A logistic system'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2010, 2011 Carlos Martín'

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

__entry_point__ = __namespace__ + ".frontends"

__requires__ = [
    __namespace__ + '.core       >= 0.1rc3',
    __namespace__ + '.components >= 0.1.90',
     ]
__tests_requires__ = [
    __namespace__ + '.core       >= 0.1rc3',
    __namespace__ + '.components >= 0.1.90',
    __namespace__ + '.testing    >= 0.1rc5',
    ]


from os import environ, path, pardir, sep
from sys import prefix

try:
    from sleipnir.core.singleton import Singleton
except:
    #pylint: disable-msg=W0702,R0903
    class Singleton(object):
        """Dummy singleton class"""
        _instance = None

        @classmethod
        def get_instance(cls):
            """Get an instance of itself"""
            cls._instance = cls._instance if cls._instance else cls()
            return cls._instance


class System(Singleton):
    """Simple class to adjust aplication location required files"""

    #pylint: disable-msg=W0231
    def __init__(self, basepath=__file__, modname=__modname__):
        #Compute prefix
        self._prefix = path.join(path.dirname(basepath), (pardir + sep) * 3)
        self._prefix = path.abspath(path.normpath(self._prefix))
        self._production = True

        if not self._prefix.startswith(prefix):
            # get Development Root dir
            self._prefix = path.join(self._prefix, pardir)
            self._prefix = path.abspath(path.normpath(self._prefix))
            self._production = False

        self._modname = modname

    def get_prefix(self):
        """Get system prefix"""
        return self._prefix

    def get_sharedir(self):
        """Get system sharedir"""
        share = 'share' if self._production else 'data'
        return path.join(self._prefix, share)

    def get_libdir(self):
        """Get python system prefix"""
        return path.join(self.get_srcdir(), __namespace__, self._modname)

    def get_srcdir(self):
        """Get source prefix"""
        return self._prefix if self._production \
            else path.join(self._prefix, 'src')

    def get_localedir(self):
        """Get locale dir prefix"""
        return path.join(self.get_sharedir(), 'locale')

    # pylint: disable-msg=R0201
    def get_configdir(self):
        """Get local config dir"""
        home = path.join(environ.get('HOME', '/'), '.config')
        home = environ.get('XDG_CONFIG_HOME', home)
        return path.join(home, __namespace__, self._modname)

    def get_uidir(self):
        """Get UI dir prefix"""
        return path.join(self.get_sharedir(), 'ui')


# pylint: disable-msg=E1101
# Common directories
__prefix__      = System.get_instance().get_prefix()
__ui_dir__      = System.get_instance().get_uidir()

# Add here more constants for this project
__gettext__    = __namespace__.lower()
__locale_dir__ = System.get_instance().get_localedir()
__config_dir__ = System.get_instance().get_configdir()
