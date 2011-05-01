##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Folder containing viewlets.

$Id: container.py 238392 2011-05-01 03:46:07Z hathawsh $
"""
from OFS.CopySupport import CopyContainer
from Products.Archetypes.public import *
from Products.CompositePack.config import PROJECTNAME
from Products.CompositePack.viewlet.interfaces import IViewlet
from Products.CompositePack.viewlet.interfaces import ILayout
from Products.CMFCore.utils import UniqueObject

class ViewletContainer(BaseFolderMixin, UniqueObject):
    """A container for registered viewlets
    """
    meta_type = portal_type = archetype_name = 'CompositePack Viewlet Container'
    schema = MinimalSchema
    global_allow = 0

    filter_content_types = 1

    allowed_content_types = ('CompositePack Viewlet',)

    content_icon = 'composite.gif'

    def all_meta_types(self):
        return BaseFolderMixin.all_meta_types(
            self, interfaces=(IViewlet,))

    def indexObject(self):
        '''viewlet container is never catalogued'''
        pass

    def reindexObject(self, idxs=[]):
        '''viewlet container is never catalogued'''
        pass

    def unindexObject(self):
        '''viewlet container is never catalogued'''
        pass

    def _verifyObjectPaste(self, object, validate_src=1):
        # Objects in this container have an incorrect __factory_meta_type__.
        # Use the implementation that uses meta_type instead.
        return CopyContainer._verifyObjectPaste(self, object,
            validate_src=validate_src)

registerType(ViewletContainer, PROJECTNAME)

class LayoutContainer(BaseFolderMixin, UniqueObject):
    """A container for registered viewlets
    """
    meta_type = portal_type = archetype_name = 'CompositePack Layout Container'
    schema = MinimalSchema
    global_allow = 0

    filter_content_types = 1

    allowed_content_types = ('CompositePack Layout',)

    factory_type_information={
            'content_icon':'composite.gif',
            }

    def all_meta_types(self):
        return BaseFolderMixin.all_meta_types(
            self, interfaces=(ILayout,))

    def indexObject(self):
        '''layout container is never catalogued'''
        pass

    def reindexObject(self, idxs=[]):
        '''layout container is never catalogued'''
        pass

    def unindexObject(self):
        '''layout container is never catalogued'''
        pass

    def _verifyObjectPaste(self, object, validate_src=1):
        # Objects in this container have an incorrect __factory_meta_type__.
        # Use the implementation that uses meta_type instead.
        return CopyContainer._verifyObjectPaste(self, object,
            validate_src=validate_src)

registerType(LayoutContainer, PROJECTNAME)
