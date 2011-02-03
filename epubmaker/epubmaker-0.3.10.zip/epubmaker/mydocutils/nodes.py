#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""

nodes.py

Copyright 2011 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Added nodes for PG.

"""

from docutils import nodes

class page (nodes.Special, nodes.Invisible, nodes.Element):
    """ Hold pagination commands. """

