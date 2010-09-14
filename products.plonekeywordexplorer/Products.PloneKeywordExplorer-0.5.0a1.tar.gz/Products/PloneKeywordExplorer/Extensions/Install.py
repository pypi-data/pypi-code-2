# -*- coding: utf-8 -*-
## PloneKeywordExplorer
## Alternative search facility using keywords
## Copyright (C)2006-2007 Ingeniweb

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

##########################################################
##                                                      ##
## INSTALL PROCEDURE FOR PloneKeywordExplorer           ##
##                                                      ##
##########################################################

from cStringIO import StringIO
import string

from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName

from Products.PloneKeywordExplorer import install_globals
from Products.PloneKeywordExplorer.global_symbols import *
from Products.PloneKeywordExplorer import TOOL


skin_name = "PloneKeywordExplorer"

product_name = "PloneKeywordExplorer"

def installSubSkin(self, out, skinFolder):
    """ Install a subskin, i.e. a folder/directoryview.
    """
    skinsTool = getToolByName(self, 'portal_skins')

    for skin in skinsTool.getSkinSelections():
        path = skinsTool.getSkinPath(skin)
        path = map( string.strip, string.split( path,',' ) )
        if not skinFolder in path:
            try:
                path.insert( path.index( 'custom')+1, skinFolder )
            except ValueError:
                path.append(skinFolder)
            path = string.join( path, ', ' )
            skinsTool.addSkinSelection( skin, path )
            out.write('Subskin successfully installed into %s.\n' % skin)    
        else:
            out.write('*** Subskin was already installed into %s.\n' % skin) 

def setupSkins(self, out):
    skinsTool = getToolByName(self, 'portal_skins')
    
    # Install de chaque nouvelle subskin/layer
    try:
        addDirectoryViews(skinsTool, LAYERS_PATH, install_globals)
        out.write( "Added directory views to portal_skins.\n" )
    except:
        out.write( '*** Unable to add directory views to portal_skins.\n')

    # Param de chaque nouvelle subskin/layer
    installSubSkin(self, out, skin_name)

def addTool(self, out) :
    # Check that the tool has not been added using its id
    if not hasattr(self, TOOL.id) :
        addTool = self.manage_addProduct[PROJECTNAME].manage_addTool
        # Add the tool by its meta_type
        addTool(TOOL.meta_type)
        out.write(TOOL.id + " tool installed")

def addActionProvider(self):
    actionsTool = getToolByName(self, 'portal_actions', None)
    actionsTool.addActionProvider(TOOL.id)
    

def install(self):
    out=StringIO()
    setupSkins(self, out)
    #setActionsTool(self, out)
    addTool(self, out)
    addActionProvider(self)
    out.write('Installation completed.\n')
    return out.getvalue()
