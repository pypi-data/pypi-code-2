# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>
                Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component.factory import Factory
from zope.i18nmessageid import MessageFactory
from AccessControl import ClassSecurityInfo
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.contentproxy.interfaces import IProxiedContentInfo
from bda.contentproxy.interfaces import IProxiedContent
from bda.contentproxy.interfaces import ContentLookupError

try:
    from Products.LinguaPlone.public import *
except ImportError:
    from Products.Archetypes.atapi import *

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
    import ReferenceBrowserWidget

import interfaces

_ = MessageFactory('bda.contentproxy')

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].required = 0
copied_fields['title'].mode = "r"
copied_fields['language'] = ExtensibleMetadataSchema['language'].copy()
copied_fields['language'].mode = "r"
schema = Schema((
    StringField(
        name='proxyreference',
        widget=ReferenceBrowserWidget(
            label="Proxy Reference",
            description=_(u"Select the reference of the content you want to proxy"),
            description_msgid=_(u'bda_contentproxy_help_proxyreference'),
            required=True,
        ),
    ),
    copied_fields['title'],
    copied_fields['language'],

),
)

ATProxiedContent_schema = BaseSchema.copy() + \
    schema.copy()

class ATProxiedContent(BaseContent, BrowserDefaultMixin):
    
    security = ClassSecurityInfo()
    implements(interfaces.IATProxiedContent)

    meta_type = 'ATProxiedContent'
    _at_rename_after_creation = True

    schema = ATProxiedContent_schema

    security.declareProtected('View', 'Title')
    def Title(self):
        id = self.getId()
        if self.checkCreationFlag():
            return id
        info = IProxiedContentInfo(self)
        try:
            target = IProxiedContent(info)
        except ContentLookupError:
            return id
        if target.content(self) is self:
            return id
        return target.content(self).Title() 

    security.declareProtected('View', 'Language')
    def Language(self):
        if self.checkCreationFlag():
            return ''
        info = IProxiedContentInfo(self)
        try:
            target = IProxiedContent(info)
        except ContentLookupError:
            return ''
        return target.content(self).Language()

registerType(ATProxiedContent, 'bda.contentproxy')
addATProxiedContent = Factory(ATProxiedContent, title=_(u"Add Content Proxy"))