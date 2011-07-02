#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Application

Main Application Component Manager
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import os
import sys

__all__ = ['Application']

# Project requirements
from sleipnir.components.components import implements, Component
from sleipnir.shell.interfaces import application

# local submodule requirements
from .import constants
#pylint: disable-msg=W0611
from .import signals


#pylint: disable-msg=R0201,W0232
class Application(Component):
    """ Main Handset Component"""

    implements(application.IApplication)

    opt_table = [
        ["", "--target", "", "Override default target", "store", "target"],
        ["", "--screen",  0, "Create window in SCREEN", "store", "screen"],

        ["", "--new_window", False,                                       \
               "Force creation of a new window", "store_true", "new"],
    ]

    @property
    def name(self):
        """Applications's shotname"""
        return constants.__modname__

    @property
    def title(self):
        """Application's name"""
        return constants.__title__

    @property
    def summary(self):
        """Application's summary"""
        return constants.__summary__

    @property
    def version(self):
        """Application's version"""
        return constants.__version__

    @property
    def copyright(self):
        """Author's details"""
        return constants.__copyright__

    @property
    def doap(self):
        """Returns description of project"""
        return """\n%s %s\n%s\n""" % self.title, self.version, self.copyright

    @property
    def runnable(self):
        """Check if application is runnable under enviroment"""
        if os.environ.get('SHLVL', 1) > 1 or 'DISPLAY' not in os.environ:
            return application.IApplication.SUGGESTED
        return application.IApplication.VALID

    def usage(self, argv):
        """Show command usage when invoked from command line"""

    #pylint: disable-msg=W0613
    def help(self, argv):
        """Returns application OPT Table"""
        return self.opt_table[:]

    def help_commands(self, command=None):
        """
        Returns help info for command parameter or a list of valid
        commands if no command is present
        """

    #pylint: disable-msg=W0613
    def commands(self, name=None):
        """Get a list of available commands for this backend"""
        return []

    def run(self, args, **kwargs):
        "Invoke application"
        # imports
        from .shell import QShell

        # handle target and application args
        appkey = constants.__appname__
        parser = self.compmgr.parser
        parser.add_child_options(appkey, self.opt_table)
        parser.parse(args, parser=appkey, recursive=-1)

        # create shell
        shell = QShell.get_instance(name=constants.__modname__.capitalize())

        # Enter Main loop
        sys.exit(shell.run(parser.remain_args, dict(parser.options)))
