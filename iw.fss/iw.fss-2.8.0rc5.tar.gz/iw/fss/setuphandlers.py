## -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from Products.CMFCore.utils import getToolByName

from iw.fss.modifier import MODIFIER_ID
from iw.fss.modifier import manage_addModifier

def thisProfileOnly(func):
    """Decorator that prevents the setup func to be used on other GS profiles.
    Usage:
    @thisProfileOnly
    def someFunc(context): ...
    """

    def wrapper(context):
        if context.readDataFile('iw.fss.txt') is None:
            return
        else:
            return func(context)
    return wrapper

@thisProfileOnly
def setupVarious(context):
    """Put here various stuff that cannot be installed with generic setup"""

    portal = context.getSite()

    # Install CMFEditions modifier for FileSystemStorage
    mtool = getToolByName(portal, 'portal_modifier')

    if not MODIFIER_ID in  mtool.objectIds():
        manage_addModifier(mtool)
