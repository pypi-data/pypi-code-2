#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
AbstractFactory

Implementation of the AbstractFactory Pattern (GOF94) idiom in Python
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from .singleton import Singleton

__all__ = ['AbstractFactory']

# local submodule requirements


class AbstractFactoryError(Exception):
    """AbstractFactory error"""


class AbstractFactory(Singleton):
    """
    Allows to internally build a valid abstract for args passsed to
    'can_handle' method of declared abstracts

    As a contract, Something smells like a Abstract sii:
      o It's registered into AbstractFactory
      o Implements a class method called 'can_handle'
    """

    ignore_subsequents = True

    def __init__(self, ex_type=AbstractFactoryError):
        super(AbstractFactory, self).__init__()
        self._backends = []
        self._ex_type = ex_type

    def create(self, *args, **kwargs):
        """Build a valid abstract"""

        for _, backend in self._backends:
            if backend.can_handle(*args, **kwargs):
                return backend.new(*args, **kwargs) \
                    if hasattr(backend, 'new')      \
                    else backend(*args, **kwargs)
        raise self._ex_type(args)

    def registry(self, backend):
        """Registry a class implementations as a candidate abstract"""

        self._backends.append(backend)
