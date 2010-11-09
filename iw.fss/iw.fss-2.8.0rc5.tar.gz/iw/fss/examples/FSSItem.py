# -*- coding: utf-8 -*-
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
"""
Demo content type with a file and an image.
$Id: FSSItem.py 65108 2008-05-19 20:23:31Z cbosse $
"""

# Zope imports
from AccessControl import ClassSecurityInfo

# Archetypes imports
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import FileField
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import TextField
from Products.Archetypes.public import FileWidget
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import PrimaryFieldMarshaller
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType

from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import ATContentTypeSchema

# Products imports
from iw.fss.config import PROJECTNAME
from iw.fss.FileSystemStorage import FileSystemStorage

BaseItemShema = Schema((
    FileField('file',
              required=False,
              primary=True,
              storage=FileSystemStorage(),
              widget=FileWidget(
                  description="Select the file to be added by clicking the 'Browse' button.",
                  description_msgid="help_file",
                  label="File",
                  label_msgid="label_file",
                  i18n_domain="plone",
                  show_content_type=False,)),
    ImageField('image',
               required=False,
               sizes={
                   'mini':(40,40),
                   'thumb':(80,80),},
               storage=FileSystemStorage(),
               widget=ImageWidget()),
    TextField('text',
              required=False,
              storage=FileSystemStorage(),
              widget=TextAreaWidget()),
    ), marshall=PrimaryFieldMarshaller())

FSSItemSchema = BaseSchema.copy() + BaseItemShema.copy()
ATFSSItemSchema = ATContentTypeSchema.copy() + BaseItemShema.copy()

class FSSItem(BaseContent):
    """A simple item using FileSystemStorage"""
    archetypes_name = portal_type = meta_type = 'FSSItem'
    schema = FSSItemSchema
    _at_rename_after_creation = True


registerType(FSSItem, PROJECTNAME)

class ATFSSItem(ATCTContent):
    """A simple item using FileSystemStorage base on ATContentypes"""
    archetypes_name = portal_type = meta_type = 'ATFSSItem'
    schema = ATFSSItemSchema
    _at_rename_after_creation = True


registerType(ATFSSItem, PROJECTNAME)
