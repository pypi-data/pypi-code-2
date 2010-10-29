# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
Register in a Plone instance
$Id: Install.py 225402 2010-10-27 16:03:38Z glenfant $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
from StringIO import StringIO

# Zope imports
from Products.Archetypes.Extensions.utils import install_subskin

# CMF imports
from Products.CMFCore.utils import getToolByName

# Products imports
from Products.PloneFilesZip.config import *
from Products.PloneFilesZip.PloneFilesZipTool import PloneFilesZipTool

def install(self):
    out = StringIO()

    # Install skin
    install_subskin(self, out, GLOBALS)

    # Install tool
    add_tool = self.manage_addProduct[PROJECTNAME].manage_addTool
    archive_tool = getattr(self, PloneFilesZipTool.id, None)
    if archive_tool is None:
        add_tool(PloneFilesZipTool.meta_type)

    # Portal archive provides actions
    atool = getToolByName(self, 'portal_actions')
    atool.addActionProvider(PloneFilesZipTool.id)

    # New action icon (see PloneFilesZipTool._actions)
    atool = getToolByName(self, 'portal_actionicons')
    atool.addActionIcon('plone', 'zip', 'files_zip_icon.png', title="Download this folder's files as ZIP archive.")
    
    # Configlets
    portal_controlpanel = getToolByName(self, 'portal_controlpanel')
    portal_controlpanel.registerConfiglet(**CONFIGLET_DEFINITION)

    out.write('Installation completed.\n')
    return out.getvalue()

def uninstall(self):
    out = StringIO()

    # Tool removal doesn't seem to be automated by QI
    atool = getToolByName(self, 'portal_actions')
    atool.deleteActionProvider(TOOL_ID)
    
    # Remove configlet
    portal_controlpanel = getToolByName(self, 'portal_controlpanel')
    portal_controlpanel.unregisterApplication(PROJECTNAME)

    # Action icon removal is not automated by QI
    atool = getToolByName(self, 'portal_actionicons')
    try:
        atool.removeActionIcon('plone', 'zip')
    except KeyError, e:
        out.write("Action icon already removed")
    
    out.write('Uninstallation completed.\n')
    return out.getvalue()
