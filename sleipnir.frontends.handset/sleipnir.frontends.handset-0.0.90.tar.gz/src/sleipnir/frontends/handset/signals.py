#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Signals

Signals factory for PySide
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import PySide.QtCore

__all__ = []

# Project requirements
from sleipnir.shell.signals import SignalFactory

# local submodule requirements


#pylint:disable-msg=W0232
class PySideSignal(SignalFactory):
    """PySide based signal factory"""

    @classmethod
    def create(cls, *args, **kwargs):
        """Creates a Signal"""
        return PySide.QtCore.Signal(*args, **kwargs)

    @classmethod
    def platform(cls):
        """Get platform technology"""
        return "PySide.QtCore"
