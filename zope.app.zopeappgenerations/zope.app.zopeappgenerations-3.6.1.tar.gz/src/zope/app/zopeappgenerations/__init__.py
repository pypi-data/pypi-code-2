##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope Application Server Generations
"""
__docformat__ = "reStructuredText"

from zope.generations.generations import SchemaManager
# BBB import
from zope.generations.utility import getRootFolder


key = 'zope.app.zopeappgenerations'


ZopeAppSchemaManager = SchemaManager(
    minimum_generation=1,
    generation=5,
    package_name=key)
