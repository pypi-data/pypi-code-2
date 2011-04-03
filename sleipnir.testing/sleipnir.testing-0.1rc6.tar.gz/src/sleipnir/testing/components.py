#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Base test classes for Sleipnir Components TestSuite"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "beta"
__version__ = "0.1"
__date__    = "1 february 2010"
__license__ = "See LICENSE file for details"

# Import here required modules
import os
import sys

from unittest import TestCase as BaseTest

__all__ = ['TestCaseLoader', 'create_docsuite']

from sleipnir.components import manager, loaders
from sleipnir.components import constants


class TestCaseLoader(BaseTest):
    """Special base test class for Components"""

    def __init__(self, *args):
        self.compmgr = manager.ComponentManager()
        super(TestCaseLoader, self).__init__(*args)

    #pylint: disable-msg=W0212,C0103
    def setUp(self):
        cls = self.__class__
        if '_manager' not in cls.__dict__:
            # instantiante a common manager for all tests and
            # load plugins
            cls._manager = manager.ComponentManager()
            loaders.LoaderManager(self._manager).load()
        # Save current components to be restored later at teardown
        from sleipnir.components.metaclass import ComponentMeta
        # Make sure we have no external components hanging around in the
        # component registry
        self.__old_registry = ComponentMeta._registry
        super(TestCaseLoader, self).setUp()

    def tearDown(self):
        # Restore the original component registry
        from sleipnir.components.metaclass import ComponentMeta
        ComponentMeta._registry = self.__old_registry


def create_docsuite(tests, set_up=None, tear_down=None):
    """
    Create a valid Unittest suite for doctest files located at 'tests'
    iterable

    All files MUST be expresed has an absolute path
    """
    #pylint: disable-msg=W0212,C0103
    def setUp(test):
        """Preapre doctest to be runned next to sleipnir code"""
        from sleipnir.components.metaclass import ComponentMeta
        test.__old_registry = ComponentMeta._registry
        # Make sure we have no external components hanging around in the
        # component registry. Finally, load all plugins
        test.manager = manager.ComponentManager()
        loaders.LoaderManager(test.manager).load()
        # if a setup was passed, call it
        if callable(set_up):
            set_up(test)

    def tearDown(test):
        """Set down generic code preapred for doctest suites"""
        # if teardown was passed, call it
        if callable(tear_down):
            tear_down(test)
        from sleipnir.components.metaclass import ComponentMeta
        ComponentMeta._registry = test.__old_registry
        del test.manager

    # return a valid suite
    from doctest import DocFileSuite
    #pylint: disable-msg=W0142
    return DocFileSuite(
        *tests, module_relative=False, setUp=setUp, tearDown=tearDown)
