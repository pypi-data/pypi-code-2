#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A Hello plugin which exports to diferent components"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "22 January 2010"
__license__ = "See LICENSE file for details"

# Add here required modules
try:
    import os
    import sys
    # pylint: disable-msg=W0611
    import sleipnir
except ImportError:
    sys.path.insert(0, (os.pardir + os.sep) * 6)
    sys.path.insert(0, (os.pardir + os.sep) * 6 + 'src')

__all__ = ['HelloWorld']

# Sleipnir dependences
from sleipnir.core.components.components import Component
from sleipnir.core.components.components import implements
from sleipnir.core.components.entrypoint import ExtensionPoint

# Plugin Iface dependences
try:
    from data.interfaces.hello import IHello
except ImportError:
    from tests.data.interfaces.hello import IHello


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
