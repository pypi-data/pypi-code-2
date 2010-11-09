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
from App.class_init import InitializeClass

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.CMFEditions.interfaces.IModifier import ISaveRetrieveModifier
from Products.CMFEditions.interfaces.IArchivist import ArchivistUnregisteredError
from Products.CMFEditions.Modifiers import ConditionalTalesModifier

from iw.fss.FileSystemStorage import FileSystemStorage

MODIFIER_ID = 'FSSModifier'

modifierAddForm = PageTemplateFile('zmi/modifier_add_form.zpt',
    globals(), __name__='modifier_add_form')

def manage_addModifier(self, REQUEST=None):
    """Add a modifier for saving versions in FileSystemStorage.
    """

    # Add modifier
    modifier = Modifier()
    id = MODIFIER_ID
    title = "A modifier for saving FileSystemStorage versions"
    wrapped = ConditionalTalesModifier(id, modifier, title)
    wrapped.edit(enabled=True, condition='python:True', title=title)
    self.register(id, wrapped)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class Modifier(object):
    """
   Save each version of an FSS file into a different file so past versions of
   files are available
    """

    __implements__ = (ISaveRetrieveModifier, )

    def beforeSaveModifier(self, obj, clone):
        for field in obj.Schema().fields():
            if not hasattr(field, "getStorage"):
                # For a field that doesn't use storage
                continue

            storage = field.getStorage()

            if not isinstance(storage, FileSystemStorage):
                continue

            rtool = getToolByName(obj, 'portal_repository')
            history = rtool.getHistory(obj)
            version = len(history)

            storage.set(
                field.getName(),
                clone.__of__(obj.aq_parent),
                field.getAccessor(obj)(),
                mimetype=field.getContentType(obj),
                field=field,
                filename=field.getFilename(obj),
                version=version)

        return {}, [], []

    def afterRetrieveModifier(self, obj, repo_clone, preserve=()):
        return [], [], {}