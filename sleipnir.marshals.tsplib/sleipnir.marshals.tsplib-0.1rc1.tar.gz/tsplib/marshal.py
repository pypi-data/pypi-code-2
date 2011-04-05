#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A marshal to build TSPLib files from/to TSPSections"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Add here required modules
import threading

from operator import iadd
from collections import deque
from StringIO import StringIO

# Sleipnir dependences
from sleipnir.components.components import implements, Component

# Sleipnir tsp
from sleipnir.heuristics.interfaces import marshal
from sleipnir.heuristics.sections import SectionFactory

__all__ = ['TSPMarshalError', 'TSPUnMarshal', 'TSPMarshal']

# Local dependences
# pylint: disable-msg=E0611
from .parser import TSPParser
from .visitor import TSPVisitor


class TSPMarshalError(Exception):
    """A custom error for TSPMarshal plugin"""


class TSPMarshal(Component):
    """
    A Stateless component to serialize TSP Problems into TSPLib files
    """
    implements(marshal.IMarshal)

    def __init__(self):
        super(TSPMarshal, self).__init__()

    def dump(self, handler, where=None):
        """Dump contents from handler into 'where'"""
        buf = StringIO() if where is None else where
        # visit buffer
        TSPVisitor(stream=buf).visit(handler)
        # compute value
        contents = buf.getvalue() if where is None else None
        buf.close()
        return contents


class TSPUnMarshal(Component):
    """
    A Stateless component to build TSP problems from a TSPlib stream
    """
    implements(marshal.IUnMarshal)

    def __init__(self):
        super(TSPUnMarshal, self).__init__()
        self._tsp = SectionFactory.get_instance().create()
        self._parser, self._qe, self._last = TSPParser(), deque(), None
        for event in self._parser.events.values():
            event.connect(self.__on_event)

        self.__mutex = threading.Lock()

    def __on_event(self, stype, value):
        """
        An event handler to hook when a new token is detected by
        internal parser
        """

        if stype in ("emptyline", 'EOF'):
            # pylint: disable-msg=W0612
            [iadd(self._tsp, self._qe.popleft()) for n in range(len(self._qe))]
            if stype == 'EOF':
                self._parser.stop()
            return
        if stype in ('comments'):
            factory = SectionFactory.get_instance()
            self._qe.append(factory.create(value, type=stype))
            return

        # create a valid section for type
        if stype in ('section', 'content'):
            self._last = sec = getattr(self._tsp, 'create_' + stype)(value)
        elif stype in ('sec_value', 'content_value'):
            sec = self._last.values.create(value)
        # Now add to TSP
        # pylint: disable-msg=W0612
        [sec.add(self._qe.popleft()) for n in range(len(self._qe))]

    def load(self, where):
        """Build a new TSP problem from 'where' contents"""

        self.__mutex.acquire()
        try:
            self._tsp = SectionFactory.get_instance().create()
            self._parser.parse(where)
        finally:
            self.__mutex.release()
        return self._tsp
