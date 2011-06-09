#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Clients Flow"""

from __future__ import absolute_import

__author__  = "Carlos Martín"
__license__ = "See LICENSE file for details"

# local submodule requirements
from ..profiles import BaseProfile


#pylint: disable-msg=R0903,W0232
class ClientProfile(BaseProfile):
    """Clients Flow"""
    PROVIDES = "clients"
    REGISTER = [[None, "STARTING", None, "IDashBoard", PROVIDES]]
