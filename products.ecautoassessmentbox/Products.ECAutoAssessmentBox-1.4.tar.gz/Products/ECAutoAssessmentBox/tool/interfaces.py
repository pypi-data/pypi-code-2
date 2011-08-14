# -*- coding: utf-8 -*-
# $Id: interfaces.py 1547 2011-04-01 07:34:35Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAutoAssessmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

from zope.interface import Interface

class IECSpoolerTool(Interface):
    """Marker interface for .ECSpoolerTool.ECSpoolerTool
    """
