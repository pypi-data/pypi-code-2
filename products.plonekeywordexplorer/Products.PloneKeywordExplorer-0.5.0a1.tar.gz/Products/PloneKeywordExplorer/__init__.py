# -*- coding: utf-8 -*-
## PloneKeywordExplorer
## Alternative search facility using keywords
## Copyright (C) 2006-2007 Ingeniweb

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

"""Plone Keyword Explorer"""

from global_symbols import *
import tool
from os.path import join

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils


registerDirectory(LAYERS_PATH, globals())
# registerDirectory('skins/PloneKeywordExplorer', globals())

install_globals = globals()          # Used only in the Extensions/Install.py script

TOOL = tool.PloneKeyWordExplorerTool

def initialize(context) :
    ## Register our tool
    utils.ToolInit(
        "%s's Tool" % PROJECTNAME,
        tools=(TOOL,),
        icon=join(SKIN_PATH, ICON),
    ).initialize(context)
