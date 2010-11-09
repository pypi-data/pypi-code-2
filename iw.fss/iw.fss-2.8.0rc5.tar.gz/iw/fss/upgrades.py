## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

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

# $Id: upgrades.py 93246 2009-07-28 16:49:10Z glenfant $
"""
GS upgrade steps for iw.fss
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from utils import IfInstalled
from zope.app.component.hooks import getSite

@IfInstalled()
def removeFSSTool(setuptool):
    """We don't need it anymore from version 2.7.3"""
    portal = getSite()
    if 'portal_fss' in portal.objectIds():
        portal._delObject('portal_fss')
    return

@IfInstalled()
def addFSSPropertySheet(setuptool):
    """Options are stored in that propertysheet"""

    setuptool.runImportStepFromProfile('profile-iw.fss:default', 'propertiestool',
                                       run_dependencies=False)
    return
