## -*- coding: utf-8 -*-
## Copyright (C)2006 Ingeniweb

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

from Products.CMFCore import DirectoryView
from Products.CMFCore import utils

from Products.LinguaFace import config

import logging
LOG = logging.getLogger("LinguaFace")

from Products.LinguaFace import LinguaFaceTool

from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.CMFPlone.utils import base_hasattr



import patches

def getCanonicalPath(obj, portal, **kwargs):
    """ Catalog helper to stop acquisition for the getCanonicalPath index """
    if base_hasattr(obj, 'getCanonicalPath'):
        return obj.getCanonicalPath()
    else:
        return obj.getPhysicalPath()

## Register our directory in Zope
DirectoryView.registerDirectory("skins", globals())

## Save the globals for use in the Plone Quick Installer
config.GLOBALS = globals()

def initialize(context) :
    # Apply catalog helper
    registerIndexableAttribute('getCanonicalPath', getCanonicalPath)

    # Apply monkey patches
    from Products.LinguaFace import patches

    ## Register our tool
    utils.ToolInit(
        "%s's Tool" % config.PROJECTNAME,
        tools=(LinguaFaceTool.LinguaFaceTool,),
        product_name=config.PROJECTNAME,
        icon='linguaface_icon.gif',
    ).initialize(context)



