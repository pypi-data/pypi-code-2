##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: public.py 238387 2011-04-30 19:58:15Z hathawsh $
"""
try:
    from Products.CompositePack.ClassGen import registerType
except ImportError:
    from Products.Archetypes.public import registerType

try:
    from Products.LinguaPlone.public import BaseContent
except ImportError:
    from Products.Archetypes.public import BaseContent

try:
    from Products.LinguaPlone.public import BaseFolder
except ImportError:
    from Products.Archetypes.public import BaseFolder
