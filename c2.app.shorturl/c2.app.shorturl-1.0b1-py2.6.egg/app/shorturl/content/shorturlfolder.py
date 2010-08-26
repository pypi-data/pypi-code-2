#!/usr/bin/env python
# encoding: utf-8
"""
shorturlfolder.py

Created by Manabu Terada on 2010-08-03.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from AccessControl import ClassSecurityInfo
#from ComputedAttribute import ComputedAttribute
from zope import interface

from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf
# from Products.CMFCore.permissions import View, ModifyPortalContent

from c2.app.shorturl import ShortUrlMessageFactory as _
from c2.app.shorturl.content.interfaces import IShortUrlFolder
from c2.app.shorturl.config import *

schema = Schema((

),)

folder_schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()
finalizeATCTSchema(folder_schema)

class ShortUrlFolder(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    interface.implements(IShortUrlFolder)
    schema = folder_schema
    
    meta_type = "ShortUrlFolder"
    _at_rename_after_creation = True

registerType(ShortUrlFolder, PROJECTNAME)