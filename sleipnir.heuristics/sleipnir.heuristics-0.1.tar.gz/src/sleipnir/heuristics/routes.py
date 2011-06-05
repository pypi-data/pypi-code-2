#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Routes

Represents a node in an TSP problem
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from array import array
from bisect import bisect
from functools import partial
from itertools import combinations, izip, ifilter
from math import sqrt
from operator import attrgetter
from threading import Lock, Event
from weakref import proxy

__all__ = ['Edge', 'Route', 'Routes', 'RouteFactory']

# Project requirements
from sleipnir.core.thread import Task
from sleipnir.core.factory import AbstractFactory

# local submodule requirements
from .locations import LocationFactory


#pylint: disable-msg=R0903,E0602,W0232
class Edge(enum):
    """Supported Edge Types"""

    UNKNOWN, DIRECTED, UNDIRECTED = xrange(0, 3)


class Route(object):
    """Main Route object"""

    def __init__(self, org, des, orientation=Edge.UNDIRECTED):
        self._org = org if orientation == Edge.DIRECTED else min(org, des)
        self._des = des if orientation == Edge.DIRECTED else max(org, des)
        self._orient = orientation
        self._rindex = (self._org, self._des, self._orient,)
        self._hashid = id(self._rindex)

    def __hash__(self):
        return self._hashid

    def __call__(self):
        return self._rindex

    def __lt__(self, other):
        return self._rindex < other._rindex

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self),)

    def __str__(self):
        drt = '->' if self._orient == Edge.DIRECTED else '<->'
        return '(%s%s%s)' % (self._org, drt, self._des,)

    @property
    def origin(self):
        """Get origin point"""
        return self._org

    @property
    def destination(self):
        """Get destination point"""
        return self._des

    @property
    def orientation(self):
        """Check if route is directed"""
        return self._orient


class Routes(object):
    """A simple container for static route methods"""

    @staticmethod
    def create(locations, orientation=Edge.DIRECTED):
        """ Create a tuple of routes based on a list of locations """
        locations = sorted(locations)
        # undirected
        if orientation == Edge.UNDIRECTED:
            combis = combinations((locations), 2)
            return [Route(org, des, orientation) for org, des in combis]
        # directed
        return [Route(org, des, orientation) \
                    for org in locations     \
                    for des in locations if org != des]

    @staticmethod
    def euclidean(route, dimensions=0):
        """Returns euclidean distance between locations"""
        pcx, pcy = route.origin.coords, route.destination.coords
        weight = (pcx[0] - pcy[0]) ** 2 + (pcx[1] - pcy[1]) ** 2
        dimensions = dimensions or len(pcx)
        if dimensions > 2:
            for i in xrange(2, dimensions):
                weight += (pcx[i] - pcy[i]) ** 2
        return sqrt(weight)

    @staticmethod
    def matrix_index(route):
        """
        Gets a valid index to a internal matrix representation based
        on origin, destination and orientation
        """
        org, des, orientation = route()
        org, des = int(org), int(des)
        if orientation == Edge.UNDIRECTED:
            if org > des:
                org, des = des, org
            des = des - org - 1
        return (org, des, orientation,)


#pylint: disable-msg=R0903,W0232,E1101
class RouteFactory(AbstractFactory):
    """Allows to internally build a valid set of routes"""


class MetaRoute(type):
    """Route Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Route"):
            RouteFactory.get_instance().registry((name, mcs))


#pylint: disable-msg=R0903
class AbstractRoute(object):
    """Base class to be used (optionally) by all routes"""

    __metaclass__ = MetaRoute

    #pylint: disable-msg=W0613
    def __init__(self):
        super(AbstractRoute, self).__init__()

        self._routes = {}
        self._routes_list = []
        self._routes_lock = Lock()
        self._routes_event = Event()
        self._routes_event.set()

    def __call__(self, value):
        raise NotImplementedError

    def __getattr__(self, value):
        if value in ('cities',):
            return self.locations
        raise AttributeError(value)

    def __iter__(self):
        return self._routes_list

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._routes)

    def __str__(self):
        return str(self._routes_list)

    def __len__(self):
        return len(self._routes)

    def __contains__(self, route):
        return route in self._routes

    def __getitem__(self, route):
        return self._routes_list[route] \
            if type(route) in (int,) else self._routes[route]

    def __enter__(self):
        self._routes_lock.acquire()
        while not self._routes_event.is_set():
            self._routes_lock.release()
            self._routes_event.wait()
            self._routes_lock.acquire()
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self._routes_lock.release()

    def update(self, routes):
        """Updates cached objects"""
        if not self._routes_list:
            self._routes_list = sorted(
                routes,
                key=attrgetter('origin', 'destination'))
        else:
            for route in ifilter(lambda x: x in self._routes, routes):
                bisect.insert(self._routes_list, route)
        # now update dict
        self._routes.update(izip(routes, routes))

    @property
    def locations(self):
        """
        Returns an iterable of locations defined on this route set
        """
        raise NotImplementedError

    @property
    def directed(self):
        """
        Returns True if graph is directed. OtherWise, returns False
        """
        raise NotImplementedError

    @classmethod
    def can_handle(cls, *args, **kwargs):
        """
        Advise if it's a valid class for arguments pased to the method
        """
        return False


class MatrixRoutes(AbstractRoute):
    """Abstract class for Routes"""

    MT, MT_FUNC, MT_DIRT = xrange(3)
    MT_TYPECODE = {
        float:   'f',
        int:     'l',
        long:    'L',
        str:     'c',
        unicode: 'u',
        }

    def __init__(self, locations, orientation):
        super(MatrixRoutes, self).__init__()
        self._drct = orientation
        self._locs = locations
        self._mtrx = {}

    def __call__(self, attr):
        if attr in self._mtrx:
            return self._mtrx[attr][self.MT]
        raise AttributeError("Unknown '%s' routes property", attr)

    def __getattr__(self, value):
        def accessor(route):
            """Gets access to attribute matrix"""
            try:
                org, des, _ = Routes.matrix_index(route)
                return self._mtrx[value][self.MT][org][des] \
                    or self._mtrx[value][self.MT_FUNC](route)
            except (KeyError, IndexError):
                raise
        if value in self._mtrx:
            return accessor
        # invoke parent
        return super(MatrixRoutes, self).__getattr__(value)

    def __setattr__(self, name, value):
        if not name[0] == '_':
            self._mtrx.setdefault(name, [None, None, None])
            self._mtrx[name][self.MT_FUNC] = value
            self._mtrx[name][self.MT_DIRT] = True
        super(MatrixRoutes, self).__setattr__(name, value)

    def __mtrx_create(self, attribute):
        """
        Create a matrix representation to store an attribute from
        route
        """
        mtrxfunc = self._mtrx[attribute][self.MT_FUNC]
        pythtype = type(mtrxfunc(self._routes_list[0]))
        typecode = self.MT_TYPECODE[pythtype]
        mtrxsize = len(self._locs)

        if self._drct == Edge.UNDIRECTED:
            return [array(typecode, [pythtype()      \
                 for col in xrange(mtrxsize - row)]) \
                 for row in xrange(mtrxsize)]
        else:
            return [array(typecode, [pythtype()      \
                 for col in xrange(mtrxsize)         \
                 for row in xrange(mtrxsize)])]

    def _mtrx_resize(self):
        """
        Resize internal matrix representations to allow to host routes
        """
        if not any(True for route in routes if route not in self._routes):
            return
        max_org = max(routes, key=attrgetter('origin'))
        max_des = max(routes, key=attrgetter('destination'))
        maxsize = max(max_org.origin, max_des.destination)

        for mtrx, _ in self._mtrx.itervalues():
            mtrx += [None] * (maxsize - len(mtrx))
            for n_row in xrange(maxsize):
                if mtrx[n_row] is None:
                    mtrx[n_row] = array(mtrx[0].typecode)
                extend_size = maxsize - len(mtrx[n_row])
                if self._drct == Edge.UNDIRECTED:
                    extend_size -= n_row - 1
                mtrx[n_row].extend([[] * extend_size])

    #pylint: disable-msg=W0102
    def update(self, routes=[], attributes=[], attr_funcs=[], clean=True):
        """Update(add) matrix attributes and routes"""

        def _update_task(self, routes, attributes, attr_funcs, wrapper):
            """Helper to update routes in background"""
            self._routes_lock.acquire()
            try:
                if routes or len(self._routes) == 0:
                    if not routes:
                        routes = Routes.create(self.locations, self._drct)
                    super(MatrixRoutes, self).update(routes)

                    # prepare elements to be updated
                    attributes = attributes or self._mtrx.keys()
                else:
                    routes = self._routes_list
                    iitems = self._mtrx.iteritems()

                    # prepare elements to be updated
                    attributes = attributes or \
                        [k for k, v in iitems if v[self.MT_DIRT]]

                # prepare attribute funcs
                if not attr_funcs:
                    atr = attributes
                    flt = ifilter(lambda x: self._mtrx[x][self.MT_DIRT], atr)
                    attr_funcs = [self._mtrx[x][self.MT_FUNC] for x in flt]

                # update now!
                for attr, func in izip(attributes, attr_funcs):
                    route = self._routes_list[0]
                    self._mtrx.setdefault(attr, [None, func, True])
                    mtrx_tuple = self._mtrx[attr]
                    if mtrx_tuple[self.MT] is None:
                        mtrx_tuple[self.MT] = self.__mtrx_create(attr)
                    for route in routes:
                        org, des, _ = Routes.matrix_index(route)
                        mtrx_tuple[self.MT][org][des] = func(route)
                    self._mtrx[attr][self.MT_DIRT] = not clean
            finally:
                self._routes_event.set()
                self._routes_lock.release()
        with self:
            func = partial(_update_task, self, routes, attributes, attr_funcs)
            self._routes_event.clear()
            Task(func).start()

    @property
    def locations(self):
        return self._locs

    @property
    def directed(self):
        return self._drct == Edge.DIRECTED


class RoutesCGfromMatrix(MatrixRoutes):
    """
    Build a set of routes based on a matrix of weights, where
    location id is expressed has matrix index
    """
    @classmethod
    def can_handle(cls, matrix, orientation=Edge.DIRECTED):
        directed = orientation == Edge.DIRECTED
        try:
            for org, des in combinations(xrange(len(matrix)), 2):
                if directed:
                    assert matrix[des][org]
                org, des = Route.matrix_index(org, des, orientation)
                assert matrix[org][des]
        except Exception:
            return False
        return True

    @classmethod
    def new(cls, matrix, orientation=Edge.UNKNOWN, **kwargs):
        """Create an instance of this class"""
        # Aggregate custom args for Route Factory
        factory = LocationFactory.get_instance()
        locations = factory.create(xrange(len(matrix)), **kwargs)
        direction = orientation or Routes.matrix_orientation(matrix)
        routes = cls(locations, direction)
        return routes


class RoutesCGfromLocs(MatrixRoutes):
    """
    Build a set of routes based on A tuple of locations
    """
    @classmethod
    def can_handle(cls, locations):
        try:
            return locations[0].coord_type.startswith("EUC_")
        except Exception:
            return False

    @classmethod
    def new(cls, *args, **kwargs):
        """Create an instance of this class"""
        # Aggregate custom args for Route Factory
        routes = cls(*args, **kwargs)
        routes.weights = Routes.euclidean
        return routes


class RoutesCGfromSection(RoutesCGfromLocs):
    """
    Build a set of routes (Complete Graph) based on A set of Euclidean
    locations
    """
    def __init__(self, section, orientation=Edge.UNDIRECTED):
        self._nodes = proxy(section.node_coord)
        locs = LocationFactory.get_instance().create(self._nodes.root)
        # now instantiate
        super(RoutesCGfromSection, self).__init__(locs, orientation)

    @classmethod
    def can_handle(cls, sections):
        try:
            edge_weight_section = sections.edge_weight.section
            return edge_weight_section.values[0].value.startswith("EUC_")
        except Exception:
            return False
