#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Decorators"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"

# Import Here any required modules for this module.
from array import array
from copy import deepcopy

__all__ = ['Cast', ]

# local submodule requirements
from .factory import AbstractFactory


#pylint: disable-msg=R0903,W0232,E1101
class Cast(AbstractFactory):
    """ Allow cast between objects, collections and primary types """

    def __getattr__(self, name):
        if name == 'get':
            return self.create


class MetaCast(type):
    """Section Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Cast"):
            Cast.get_instance().registry((name, mcs))


class MatrixCast(object):
    """Base class for Matrix castings"""

    __metaclass__ = MetaCast

    def __init__(self, instance):
        self._value = instance
        self._typec = {
            float:   'f',
            int:     'l',
            long:    'L',
            str:     'c',
            unicode: 'u',
            }


class MatrixObjectToArray(MatrixCast):
    """Cast an object accessible as a matrix [][] to an true array"""

    def __getattr__(self, name):
        value = getattr(self._value[0][0], name)
        return [array(self._typec[type(value)], [                  \
                    getattr(self._value[row][col], name)           \
                        for col in xrange(len(self._value[row]))]) \
                    for row in xrange(len(self._value))]

    @classmethod
    def can_handle(cls, instance):
        """Check if cand handle instance"""
        valid = False
        # pylint: disable-msg=W0150
        try:
            if not hasattr(instance, '__call__'):
                _ = instance[len(instance) - 1]
                [child[len(child) - 1] for child in instance]
                valid = True
        finally:
            return valid


class MatrixRouteToArray(MatrixCast):
    """Cast an object accessible as a matrix [][] to an true array"""

    def __getattr__(self, name):
        for name in (name, name + 's',):
            #pylint: disable-msg=W0703
            try:
                if self._value.directed:
                    return deepcopy(self._value(name))

                # transform on a full matrix
                value, mtrx = self._value(name)[0][0], self._value(name)
                typecode = self._typec[type(value)]
                pythtype = type(value)
                mtrxsize = len(mtrx)

                # create a SxS matrix with default values
                nwmtrx =                                  \
                [array(typecode, [pythtype()] * mtrxsize) \
                     for row in xrange(mtrxsize)]

                # copy contents
                for org in xrange(mtrxsize):
                    for des in xrange(len(mtrx[org]) - 1):
                        col = org + des + 1
                        nwmtrx[org][col] = nwmtrx[col][org] = mtrx[org][des]
                return nwmtrx
            except Exception:
                pass
        raise AttributeError("Unknown '%s' named array", name)

    @classmethod
    def can_handle(cls, instance):
        """Check if cand handle instance"""
        iterable = instance.__class__.__mro__
        return any((cls for cls in iterable if cls.__name__ == 'MatrixRoutes'))
