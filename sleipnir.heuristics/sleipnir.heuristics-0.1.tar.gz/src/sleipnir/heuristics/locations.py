#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Locations

Represents a node in an TSP problem
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from weakref import proxy

__all__ = ['LocationFactory']

# local submodule requirements
from sleipnir.core.factory import AbstractFactory


#pylint: disable-msg=R0903,W0232,E1101
class LocationFactory(AbstractFactory):
    """Allows to internally build a valid set of locations"""


class MetaLocation(type):
    """Location Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Locations"):
            LocationFactory.get_instance().registry((name, mcs))


#pylint: disable-msg=R0903
class AbstractLocation(object):
    """Base class to be used (optionally) by all locations"""

    __metaclass__ = MetaLocation

    #pylint: disable-msg=W0613
    def __init__(self, **kwargs):
        super(AbstractLocation, self).__init__()
        self._value = None

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._value)

    def __str__(self):
        return str(self._value)

    def __len__(self):
        return len(self._value)

    def __getitem__(self, index):
        return self._value[index]

    def __call__(self, lid):
        iid = lid - 1
        if iid < len(self._value) and int(self._value[iid]) == lid:
            return self._value[iid]
        return None

    @classmethod
    def can_handle(cls, *args, **kwargs):
        """
        Advise if it's a valid class for arguments pased to the method
        """
        return False


class Coord(enum):
    """Supported Coordinate Types"""

    UNDEFINED, EUC_1D, EUC_2D, EUC_3D = xrange(4)


class Location(object):
    """Main location object"""

    def __init__(self, location_id, index=None):
        self._id = int(location_id)
        self._index = index or self._id - 1
        self.set_coords(0, 0, 0, 'UNDEFINED')

    def __int__(self):
        return self._index

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    def __str__(self):
        sta = '{%s' % (self._id)
        cor_sta = ': [%s, %s' % (self._xpos, self._ypos)
        cor_end = ']' if self._coor is Coord.EUC_2D else ', %s]' % self._zpos
        end = '}'
        return sta + cor_sta + cor_end + end if int(self._coor) else sta + end

    def set_coords(self, xpos, ypos, zpos=0, coor='EUC_2D'):
        """Set coordinated for Location"""
        self._xpos = float(xpos)
        self._ypos = float(ypos)
        self._zpos = float(zpos)
        self._coor = Coord(coor)

    @property
    def id(self):
        """Get id for this location"""
        return self._id

    @property
    def coords(self):
        """Get coordinates for Location"""
        coords = [self._xpos, self._ypos]
        if self._coor is Coord.EUC_3D:
            coords.append(self._zpos)
        return coords

    @property
    def coord_type(self):
        """Get coordinates type"""
        return self._coor

    @classmethod
    def from_euclidean(cls, location_id, xpos, ypos, zpos=0, coor='EUC_2D'):
        """Creates a Location Object from a Euclidean position"""

        location = cls(location_id)
        location.set_coords(xpos, ypos, zpos, coor)
        return location


class LocationsIter(AbstractLocation):
    """
    Build a set of cities based on a set of city ids provided by an
    iterable
    """
    def __init__(self, iterable):
        super(LocationsIter, self).__init__()
        self._value = [Location(i) for i in iterable]

    @classmethod
    def can_handle(cls, iterable):
        try:
            for lid in iterable:
                if type(lid) not in (int,):
                    return False
        except Exception:
            return False
        return True


class LocationsEUC2D(AbstractLocation):
    """
    Build a set of cities based on A set of Euclidean 2D coordinates
    """
    def __init__(self, section):
        super(LocationsEUC2D, self).__init__()
        self._nodes = proxy(section.node_coord)
        self._dirty = True
        self._update()

    def _update(self):
        if self._dirty:
            self._value = self._nodes.content.values(
                lambda x: Location.from_euclidean(*x.split()))
            self._dirty = False
        return self._value

    @classmethod
    def can_handle(cls, sections):
        try:
            return sections.edge_weight.section.values[0].value == "EUC_2D"
        except Exception:
            return False
