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

#Imports for cut, copy and delete
from urllib import quote, unquote
from OFS import Moniker
from zlib import compress, decompress
from marshal import loads, dumps
from OFS.CopySupport import CopyContainer
from Products.CMFPlone.interfaces.Translatable import ITranslatable
from Products.CMFPlone.utils import base_hasattr

manage_pasteObjects = CopyContainer.manage_pasteObjects

def _cb_encode(d):
    return quote(compress(dumps(d), 9))

def _cb_decode(s):
    return loads(decompress(unquote(s)))

def objectCopiedEvent(object, event=None):
    """ Is used to pass the original object to objectClonedEvent.
    """
    ob = object.object
    ob.original = object.original

def objectClonedEvent(object,event=None):
    """ This event is notified during the manage_pasteObjects and is used in
    in order to copy all the translations of an object at once.
    """
    ob = object.object
    orig_ob = ob.original
    del ob.original

    if base_hasattr(ob, "_first_object_to_paste"):
        #Second pass : translations that were added during the first pass
        orig_ob._first_object_to_paste._copy[orig_ob] = ob
        del orig_ob._first_object_to_paste
        del ob._first_object_to_paste
    elif base_hasattr(ob, "getOtherTranslations"):
        #First pass
        ob._copy = {}
        ob._copy[orig_ob] = ob
        oblist = orig_ob.getOtherTranslations()
        for object in oblist:
            object._first_object_to_paste = ob
        new_oblist = []
        for object in oblist:
            m=Moniker.Moniker(object)
            new_oblist.append(m.dump())
        oblist = new_oblist
        cb_copy_data = _cb_encode((0,oblist))
        #Use the manage_pasteObjects method with the translation
        manage_pasteObjects(ob.aq_parent, cb_copy_data)
        #ob._copy is now full with all the translations and their copy
        #and we can now reference the copied translations together.
        copy = ob._copy
        del ob._copy
        for translation in copy:
            if not translation.isCanonical():
                copy[translation].addTranslationReference(copy[translation.getCanonical()])

def objectMovedEvent(object,event=None):
    """ This event is notified during the manage_pasteObjects and is used in
    in order to cut/paste all the translations of an object at once.
    """
    ob = object.object
    oldParent = object.oldParent
    oldName = object.oldName
    newParent = object.newParent
    newName = object.newName
    dont_move = False
    if base_hasattr(newParent,"_v__dont_move_translations__") :
        dont_move = True

    if oldParent == None and oldName == None:
        #this is a translation so we do nothing
        return

    if newName == None and newParent == None:
        #this is a delete so we do nothing
        return

    if oldParent == newParent:
        #this is a rename so we do nothing
        return

    if base_hasattr(ob,"_v__translation_to_remove__"):
        #second pass
        del ob._v__translation_to_remove__
        return

    if base_hasattr(ob, "getOtherTranslations") and not(dont_move) :
        #first pass
        oblist = ob.getOtherTranslations()
        for object in oblist:
            object._v__translation_to_remove__ = False
        new_oblist = []
        for object in oblist:
            m=Moniker.Moniker(object)
            new_oblist.append(m.dump())
        oblist = new_oblist
        cb_copy_data = _cb_encode((1,oblist))
        #Use the manage_pasteObjects method with the translations
        manage_pasteObjects(newParent, cb_copy_data)

def objectWillBeRemovedEvent(object, event=None):
    """This handler is called before deleting object"""

    if not ITranslatable.isImplementedBy(object):
        return

    # If canonical is deleted reindex all translations on getCanonicalPath
    if not object.isCanonical():
        return

    # Set translations in a volatile to access it after object has been deleted
    object._v_translations = object.getTranslations()

def objectRemovedEvent(object, event=None):
    """This handler is called after object has been deleted"""

    if not ITranslatable.isImplementedBy(object):
        return

    # Canonical has been deleted reindex all translations on getCanonicalPath
    translations = getattr(object, "_v_translations", {})

    if not translations:
        return

    for lang, value in translations.items():
        translation = value[0]

        # Never reindex removed object
        if translation is object:
            continue

        translation.reindexObject(idxs=['getCanonicalPath'])

    # Delete volatile. We don't need it
    delattr(object, "_v_translations")
