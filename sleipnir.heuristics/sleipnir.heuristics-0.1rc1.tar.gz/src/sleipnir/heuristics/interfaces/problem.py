#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""TSP problem Interfaces"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['IProblem', ]

# Project Dependences
from sleipnir.components.entrypoint import Interface


class IProblem(Interface):
    """
    Base interface required to be implemented by TSP related problems
    """

    @property
    def sections(self):
        """Returns low level definition of the problem"""
        raise NotImplementedError

    @property
    def solutions(self):
        """returns collection of solutions for this kind of problem"""
        raise NotImplementedError

    @property
    def routes(self):
        """returns a list of routes(edges) which compose TSP problem"""
        raise NotImplementedError

    @property
    def locations(self):
        """returns a list of locations(nodes) which compose TSP problem"""
        raise NotImplementedError

    def shuffle(**kwargs):
        """
        Create a random problem based on method arguments
        """
        raise NotImplementedError

    def load_from(self, where):
        """
        Parse a TSP problem loaded from 'where' param

        Keyword arguments:
        where -- location of the problem. It could be a path to a
        file, a stream or a file descriptor
        """
        raise NotImplementedError

    def async_load_from(self, where, **kwargs):
        """Parse a TSP problem into it's own thread"""
        raise NotImplementedError
