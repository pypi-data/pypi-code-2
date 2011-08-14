# -*- coding: utf-8 -*-
# $Id: interfaces.py 1542 2011-04-01 07:13:53Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

from zope.interface import Interface

class IECLecture(Interface):
    """
    Marker interface for .ECLecture.ECLecture
    """
