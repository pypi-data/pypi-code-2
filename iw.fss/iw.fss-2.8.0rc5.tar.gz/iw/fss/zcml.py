## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

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

# $Id: zcml.py 65108 2008-05-19 20:23:31Z cbosse $
"""
ZCML fss namespace handling, see meta.zcml
"""
__author__  = 'glenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import logging
from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, PythonIdentifier

import config
from FileSystemStorage import FileSystemStorage

class ITypeWithFSSDirective(Interface):
    """Schema for fss:typeWithFSS directive"""

    class_ = GlobalObject(
        title=u'Class',
        description=u'Dotted name of class of AT based content type using FSS',
        required=True)

    fields = Tokens(
        title=u'Fields',
        description=u'Field name or space(s) separated field names',
        value_type=PythonIdentifier(),
        required=True)


def typeWithFSS(_context, class_, fields):
    """Register our monkey patch"""

    _context.action(
        discriminator=(class_.__module__,class_.__name__),
        callable=patchATType,
        args=(class_, fields)
        )


logger = logging.getLogger(config.PROJECTNAME)
LOG = logger.info

def patchATType(class_, fields):
    """Processing the type patch"""
    global patchedTypesRegistry

    for fieldname in fields:
        field = class_.schema[fieldname]
        former_storage = field.storage
        field.storage = FileSystemStorage()
        field.registerLayer('storage', field.storage)
        if patchedTypesRegistry.has_key(class_):
            patchedTypesRegistry[class_][fieldname] = former_storage
        else:
            patchedTypesRegistry[class_] = {fieldname: former_storage}
        LOG("Field '%s' of %s is stored in file system.", fieldname, class_.meta_type)
    return

# We register here the types that have been patched for migration purpose
patchedTypesRegistry = {
    # {content class : {field name: storage, ...}, ...}
    }
