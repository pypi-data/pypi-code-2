# -*- coding: utf-8 -*-
## ProductName
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
"""
 **************************************************
 ** (Un)installer for a new skin in portal skins **
 **************************************************

 Example:

     ...
     layers = ('custom', 'my_layer', 'epoz', ...)
     si = SkinInstaller('Business', new_layers=layers, is_default=1)
     ...

"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: SkinInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


from Products.CMFCore.DirectoryView import addDirectoryViews

from utils import InstallerBase

__all__ = ('SkinInstaller',)

class SkinInstaller(InstallerBase):

    _installerTitle = "skin in portal skins"


    def __init__(self, skin_name, layers_dir='skins', new_layers=(), is_default=0, **kw):
        """Constructor
        @param skin_name: skin name to be installed
        @param layers_dir: subdirectory of the Product that contains the layers
        @param new_layers: odered sequence of layers to push before 'custom'
        @param is_default: set this skin as default skin
        @param kw: override defaults like stop_on_error attribute
        """
        self.skin_name = skin_name
        self.layers_dir = layers_dir
        self.new_layers = new_layers
        self.is_default = is_default
        for k, v in kw.items():
            setattr(self, k, v)
        return


    def doInstall(self, context):
        """Process installation of new skin
        @param context: InstallationContext object
        """
        def commonItems(s1, s2):
            """Returns items in both sequences s1 and s2
            """
            result = []
            for item in s1:
                if item in s2:
                    result.append(item)
            return result

        installed_skins = context.portal_skins.getSkinSelections()
        if not self.skin_name in installed_skins:
            addDirectoryViews(context.portal_skins, self.layers_dir, context.product_globals)
            # Make [['layer1', 'layer2', ...], ['layer1', 'layer2', ...]]
            paths = [x[1] for x in context.portal_skins.getSkinPaths()]
            paths = [x.split(',') for x in paths]
            paths = [[x.strip() for x in path] for path in paths]
            # Find common layers of all skins
            paths = reduce(commonItems, paths)
            for layer in self.new_layers:
                if layer not in paths:
                    paths.insert(paths.index('custom') + 1, layer)
            paths = ','.join(paths)
            context.portal_skins.addSkinSelection(self.skin_name, paths)
            context.logInfo("Skin '%s' installed in portal skins properties" % self.skin_name)
            if self.is_default:
                context.portal_skins.default_skin = self.skin_name
                context.logInfo("And is the default skin")
        else:
            context.logWarning("There is already a skin named '%s', skipped" % self.skin_name)
        return


    def doUninstall(self, context):
        """Remove a skin
        @param context: InstallationContext object
        """
        context.portal_skins.manage_skinLayers(chosen=(self.skin_name,), del_skin=1)
        context.logInfo("Skin '%s' deleted from portal skins properties" % self.skin_name)
        if context.portal_skins.default_skin == self.skin_name:
            context.portal_skins.default_skin = 'Plone Default'
            context.logInfo("Default skin reset")
        return
