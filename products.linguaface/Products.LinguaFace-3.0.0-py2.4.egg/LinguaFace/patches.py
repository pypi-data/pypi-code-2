## -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb

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

from Products.Archetypes.BaseObject import BaseObject

from zope.component import adapts
from zope.interface import implements
from Acquisition import aq_inner, aq_parent

#Imports for delete
from OFS.ObjectManager import ObjectManager
_getOb = ObjectManager._getOb
_delOb = ObjectManager._delOb
_marker = []

#Patch I18NBaseObject
from AccessControl import ClassSecurityInfo
from Products.LinguaPlone import permissions
from Products.LinguaPlone.config import KWARGS_TRANSLATION_KEY, RELATIONSHIP
from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import isDefaultPage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from plone.locking.interfaces import ILockable
from zope.interface import Interface, classImplements
from zope.app.traversing.adapters import Traverser
from interface import ITranslatable
from Products.Archetypes.utils import shasattr

security = ClassSecurityInfo()

security.declareProtected(permissions.View, 'getCanonicalPath')
def getCanonicalPath(self):
    """ Return a path going only through canonical folders.  """
    if base_hasattr(self.aq_inner.aq_parent, 'getCanonicalPath'):
        path = self.aq_inner.aq_parent.getCanonicalPath()
        path += (self.getCanonical().id,)
        return path
    else:
        return self.getCanonical().getPhysicalPath()

security.declareProtected(permissions.AccessContentsInformation, 'myGetTranslations')
def myGetTranslations(self):
    """ Return a table containting all the translations
    """
    languages = self.getTranslationLanguages()
    return [self.getTranslation(language) for language in languages]

security.declareProtected(permissions.AccessContentsInformation, 'getOtherTranslations')
def getOtherTranslations(self):
    """ Return a table containting all the translations
    """
    languages = self.getTranslationLanguages()
    languages.remove(self.getLanguage())
    return [self.getTranslation(language) for language in languages]

security.declareProtected(permissions.AddPortalContent, 'newAddTranslation')
def newAddTranslation(self, language, *args, **kwargs):
    """Add a translation patched for LinguaFace events handlers
       Just add a '_v__dont_move_translations__' volatile attribute
       when moving contents during folder translations."""
    canonical = self.getCanonical()
    parent = aq_parent(aq_inner(self))
    req = getattr(self, 'REQUEST', None)
    if ITranslatable.providedBy(parent):
        parent = parent.getTranslation(language) or parent
    if self.hasTranslation(language):
        translation = self.getTranslation(language)
        raise AlreadyTranslated, translation.absolute_url()
    id = canonical.getId()
    while not parent.checkIdAvailable(id):
        id = '%s-%s' % (id, language)
    kwargs[KWARGS_TRANSLATION_KEY] = canonical
    if kwargs.get('language', None) != language:
        kwargs['language'] = language
    o = _createObjectByType(self.portal_type, parent, id, *args, **kwargs)
    # If there is a custom factory method that doesn't add the
    # translation relationship, make sure it is done now.
    if o.getCanonical() != canonical:
        o.addTranslationReference(canonical)
    self.invalidateTranslationCache()
    # Copy over the language independent fields
    schema = canonical.Schema()
    independent_fields = schema.filterFields(languageIndependent=True)
    for field in independent_fields:
        accessor = field.getEditAccessor(canonical)
        if not accessor:
            accessor = field.getAccessor(canonical)
        data = accessor()
        translation_mutator = getattr(o, field.translation_mutator)
        translation_mutator(data)
    # If this is a folder, move translated subobjects aswell.
    if self.isPrincipiaFolderish:
        moveids = []
        for obj in self.objectValues():
            if ITranslatable.providedBy(obj) and \
                       obj.getLanguage() == language:
                lockable = ILockable(obj, None)
                if lockable is not None and lockable.can_safely_unlock():
                    lockable.unlock()
                moveids.append(obj.getId())
        if moveids:
            o._v__dont_move_translations__= True
            o.manage_pasteObjects(self.manage_cutObjects(moveids))
            delattr(o, "_v__dont_move_translations__")
    o.reindexObject()
    if isDefaultPage(canonical, self.REQUEST):
        o._lp_default_page = True


security.declareProtected(permissions.ModifyPortalContent, 'newSetLanguage')
def newSetLanguage(self, value, **kwargs):
    """Sets the language code .

    When changing the language in a translated folder structure,
    we try to move the content to the existing language tree.

    Method patched for LinguaFace events handlers
    Just add a '_v__dont_move_translations__' volatile attribute
    when moving contents during folder translations.

    """
    translation = self.getTranslation(value)
    if self.hasTranslation(value):
        if translation == self:
            return
        else:
            raise AlreadyTranslated, translation.absolute_url()
    self.getField('language').set(self, value, **kwargs)

    # If we are called during a schema update we should not be deleting
    # any language relations.
    req = getattr(self, 'REQUEST', None)
    if shasattr(req, 'get'):
        if req.get('SCHEMA_UPDATE', None) is not None:
            return

    if not value:
        self.deleteReferences(RELATIONSHIP)

    parent = aq_parent(aq_inner(self))
    if ITranslatable.providedBy(parent):
        new_parent = parent.getTranslation(value) or parent
        if new_parent != parent:
            info = parent.manage_cutObjects([self.getId()])
            new_parent._v__dont_move_translations__= True
            new_parent.manage_pasteObjects(info)
            delattr(new_parent, "_v__dont_move_translations__")
    self.reindexObject()
    self.invalidateTranslationCache()

I18NBaseObject.getCanonicalPath = getCanonicalPath
I18NBaseObject.myGetTranslations = myGetTranslations
I18NBaseObject.getOtherTranslations = getOtherTranslations
I18NBaseObject.old_addTranslation = I18NBaseObject.addTranslation
I18NBaseObject.addTranslation = newAddTranslation
I18NBaseObject.old_setLanguage = I18NBaseObject.setLanguage
I18NBaseObject.setLanguage = newSetLanguage

# allow new methods through interface (TODO :  a more clean thing)
classImplements(I18NBaseObject, ITranslatable)

