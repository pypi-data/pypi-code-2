# -*- coding: utf-8 -*-
# $Id: alias.py 1790 2011-03-27 18:32:03Z ajung $

from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.ATContentTypes.content.link import ATLink

from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from vs.alias.config import *
from vs.alias.interfaces import IAlias
from vs.alias import AliasMessageFactory as _

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from string import strip
from urllib import quote

try:
    from Products.LinguaPlone.public import *
except ImportError:
    from Products.Archetypes.atapi import *

AliasSchema = ATLink.schema.copy() 
del AliasSchema['remoteUrl']
# referenzen nach vorn und multiple weg
AliasSchema['relatedItems'].multiValued = False
AliasSchema['relatedItems'].required = True
AliasSchema['relatedItems'].widget.label = _(u'vs_label_alias',default='Target object')
AliasSchema['relatedItems'].widget.description = _(u'vs_help_alias',default='')
AliasSchema.changeSchemataForField('relatedItems', 'default')

class Alias(ATLink):
    """
    """
    security = ClassSecurityInfo()
    implements(IAlias)
    
    meta_type = 'Alias'
    _at_rename_after_creation = True
    schema = AliasSchema
    remoteUrl =""

    security.declareProtected(View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """output
        """
        value = '' # ensure we have a string
        alias = self.getRelatedItems()
        if alias:
            reference_tool = getToolByName(self, 'reference_catalog')
            obj = reference_tool.lookupObject(alias.UID())
            if obj:
                return obj.absolute_url()
        return ""



registerType(Alias, PROJECTNAME)

