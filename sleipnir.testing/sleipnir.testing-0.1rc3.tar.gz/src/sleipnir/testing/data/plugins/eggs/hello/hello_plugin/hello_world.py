#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A Hello plugin which exports to diferent components"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "22 January 2010"
__license__ = "See LICENSE file for details"

# Plugin Iface dependences
import sys
from sleipnir.testing import constants

# Add path to Plugin Interfaces
try:
    sys.path.insert(0, constants.__data_dir__)
    from interfaces.hello import IHello
except ImportError:
    raise

__all__ = ['HelloWorld']

# Sleipnir dependences
from sleipnir.components.entrypoint import ExtensionPoint
from sleipnir.components.components import Component, implements


#pylint: disable-msg=R0903
class Hello(Component):
    """IHello implementation"""

    implements(IHello)

    def __init__(self):
        super(Hello, self).__init__()

    def hello(self, name):
        """Implements IHello.hello method"""
        return "Hello %s. Welcome to World! %s" % name, id(self)


class HelloWorld(Component):
    """Hello Frontend"""

    backends = ExtensionPoint(IHello)

    def __init__(self):
        super(HelloWorld, self).__init__()

    def salut(self):
        """Frontend Method"""
        return [backend.hello("world") for backend in self.backends]
