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
 **************************************
 ** (Un)installer for ATContentTypes **
 **************************************

 Example:

 ati = ATTypesInstaller() # Minimal: All packages from this product
 ati = ATTypesInstaller(
     package_name='SomePloneStuff',# Another package
     excluded_types=('Favorite', 'Topic'), # Types not addable
     project_type_map=[('Document', 'Memo'), # Substitute type names
                       ('Event', 'Meeting')])

 Module extending PloneInstallation to allow doing AT-based types
 installations (the standard now) following the exact protocol.

"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: ATInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


# PI imports
from utils import InstallerBase

__all__ = ('ATTypesInstaller',)


from Products.CMFCore.utils import getToolByName

# AT imports
from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes
#from Products.ATContentTypes.Extensions.utils import registerTemplates



class ATTypesInstaller(InstallerBase):
    """Handles the installation of project AT types"""

    _installerTitle = "AT-based types in portal types"


    def __init__(self, package_name=None, excluded_types=(), project_types_map=[], **kw):
        """Constructor
        @param package_name: the target AT package name (default: the current package)
        @param exclused_types: a sequence of portal_types to be removes (from addables)
        @param project_types_map: a sequence of tuples for renaming portal_types in the form:
                                  [(old_portal_type, new_portal_type), ...]
        @param kw: override defaults like stop_on_error attribute
        """

        self.package_name = package_name
        self.excluded_types = excluded_types
        self.project_types_map = project_types_map

        for k, v in kw.items():
            setattr(self, k, v)
        return


    def _backupTypes(self, context):
        # we need to exclude some types but keep them at hand !
        ttool = context.portal_types

        for type_id in self.excluded_types:
            if type_id in ttool.objectIds():
                new_id = "TMP %s" % type_id
                ttool.manage_renameObject(type_id, new_id)

                # also disable the type
                type_obj = getattr(ttool, new_id)
                type_obj.global_allow = 0

                info = 'Type %s renamed to %s, and disabled' % (type_id, new_id)
                context.logInfo(info)
        return


    def _restoreTypes(self, context):
        # reintroduce types that were backed up !
        ttool = context.portal_types

        for type_id in self.excluded_types:
            curr_id = "TMP %s" % type_id
            if curr_id in ttool.objectIds():
                ttool.manage_renameObject(curr_id, type_id)

                # also re-enable the type
                type_obj = getattr(ttool, type_id)
                type_obj.global_allow = 1

                info = 'Previous type %s restored' % type_id
                context.logInfo(info)
        return


    def _plonifyProjectTypes(self, context):
        ttool = context.portal_types

        for type_tuple in self.project_types_map:
            if type_tuple[0] in ttool.objectIds():
                old_type_id = type_tuple[0]
                new_type_id = type_tuple[1]
                if not new_type_id in ttool.objectIds():
                    ttool.manage_renameObject(old_type_id, new_type_id)
                    info = '%s : %s' % (old_type_id, new_type_id)
                    context.logInfo(info)
        return


    def _removeProjectTypes(self, context):
        ttool = context.portal_types

        for type_tuple in self.project_types_map:
            curr_type_id = type_tuple[1]
            if curr_type_id in ttool.objectIds():
                type_obj = getattr(ttool, curr_type_id)
                if type_obj.content_meta_type == type_tuple[0]:
                    ttool.manage_delObjects([curr_type_id])
                    info = 'Removed type %s' % curr_type_id
                    context.logInfo(info)
        return


    def doInstall(self, context):
        """Registers the AT-based types in portal_types
        @param context: InstallationContext object
        """
        if self.package_name is None:
            self.package_name = context.productName()

        types = listTypes(self.package_name)    # Calling AT functions here !

        installTypes(context.portal, context.report, types, self.package_name)

        # bind templates for TemplateMixin
        registerTemplates(context.portal, types, context.report)

        if self.excluded_types:
            self._backupTypes(context)
            context.logInfo('Types exclusion completed')
            get_transaction().commit(1)            # This is needed to make the following code work !

        if self.project_types_map:
            self._plonifyProjectTypes(context)
            context.logInfo('Renamed project types to their Plone-compliant names')
        return


    def doUninstall(self, context):
        """Processes the installation (Defered to a subclass)
        @param context: InstallationContext object
        """

        # Rename back project types
        if self.project_types_map:
            self._removeProjectTypes(context)
            context.logInfo('Removed project types')
            get_transaction().commit(1)

        # Restore previous types
        if self.excluded_types:
            self._restoreTypes(context)
            context.logInfo('Previous types restored')
        return

# End ATInstaller.py

#
# Copied from
# Products.ATContentTypes.Extensions.utils import registerTemplates
# in plone 2.0x. Doesn't seem to exist in ATContentTypes for Plone 2.1
#
def registerTemplates(self, typeInfo, out):
    """Registers templates in the archetypes tool
    """
    for t in typeInfo:
        klass          = t['klass']
        portal_type    = klass.portal_type
        registerTemplatesForClass(self, klass, portal_type)


def registerTemplatesForClass(self, klass, portal_type):
    atTool       = getToolByName(self, 'archetype_tool')
    default_view = getattr(klass, 'default_view', 'base_view')
    suppl_views  = getattr(klass, 'suppl_views', ())
    views        = ['base_view',]

    if default_view != 'base_view':
        atTool.registerTemplate(default_view)
        views.append(default_view)

    for view in suppl_views:
        atTool.registerTemplate(view)
        views.append(view)

    atTool.bindTemplate(portal_type, views)