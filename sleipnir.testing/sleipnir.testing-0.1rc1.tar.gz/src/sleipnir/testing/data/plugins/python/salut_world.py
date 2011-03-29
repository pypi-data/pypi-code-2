#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A Salut plugin which exports to diferent components"""

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
    sys.path.insert(0, (os.pardir + os.sep) * 5)
    sys.path.insert(0, (os.pardir + os.sep) * 5 + 'src')

__all__ = ['SalutWorld', 'Salut']

# Sleipnir dependences
from sleipnir.core.components.components import Component
from sleipnir.core.components.components import implements
from sleipnir.core.components.entrypoint import ExtensionPoint

# Plugin Iface dependences
try:
    from data.interfaces.salut import ISalut
except ImportError:
    from tests.data.interfaces.salut import ISalut


class StatefulSalut(Component):
    """Stateful ISalut implementation"""

    implements(ISalut)

    def __init__(self):
        super(StatefulSalut, self).__init__()

    def hello(self, name):
        """Implements IHello.hello method"""
        return "Salut %s from %s!" % name, id(self)


class Salut(Component):
    """Salut Frontend"""

    backends = ExtensionPoint(ISalut)

    def __init__(self):
        super(SalutWorld, self).__init__()

    def salut(self):
        """Frontend method"""
        return [backend.hello("world") for backend in self.backends]
