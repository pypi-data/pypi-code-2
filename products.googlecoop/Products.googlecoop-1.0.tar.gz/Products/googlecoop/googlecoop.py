# -*- coding: utf-8 -*-
#
# File: googlecoop.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 1.6.0-beta-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Christian Ledermann <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.googlecoop.config import *


from Products.CMFCore.utils import UniqueObject

    
##code-section module-header #fill in your manual code here
import md5
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
##/code-section module-header

schema = Schema((

    StringField(
        name='identifier',
        default="009744842749537478185:hwbuiarvsbo",
        widget=StringWidget(
            description="Your Custom Search Engine's unique identifier",
            label="Identifier",
            label_msgid='googlecoop_label_identifier',
            description_msgid='googlecoop_help_identifier',
            i18n_domain='googlecoop',
        ),
        required=True,
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='adsposition',
        widget=SelectionWidget(
            label="Show ads on results pages",
            description="Specify where in the results you want advertising to be placed.",
            label_msgid='googlecoop_label_adsposition',
            description_msgid='googlecoop_help_adsposition',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        vocabulary='getAdsVocabulary',
        default='FORID:9',
        required=True,
        write_permission="Manage Portal"
    ),

    StringField(
        name='domain',
        default="www.google.com",
        widget=StringWidget(
            label="Google Domain",
            description="You can choose a different Google domain than google.com (such as google.ru or google.es). This makes your search results favor results from that country.",
            label_msgid='googlecoop_label_domain',
            description_msgid='googlecoop_help_domain',
            i18n_domain='googlecoop',
        ),
        required=True,
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='addStatus',
        widget=SelectionWidget(
            label="Advertising status",
            description="Specify whether your search engine is for a non-profit, university, or government website that should not have advertising on the results pages.",
            label_msgid='googlecoop_label_addStatus',
            description_msgid='googlecoop_help_addStatus',
            i18n_domain='googlecoop',
        ),
        multiValued=False,
        vocabulary='getAddStatusVocabulary',
        default="false",
        required=True,
        write_permission="Manage Portal",
        read_permission="View"
    ),

    BooleanField(
        name='labelKeywords',
        default="False",
        widget=BooleanField._properties['widget'](
            label="Use Keywords",
            description="Use your sites keywords as labels for the CSE",
            label_msgid='googlecoop_label_labelKeywords',
            description_msgid='googlecoop_help_labelKeywords',
            i18n_domain='googlecoop',
        ),
        required=True,
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='borderColor',
        default=336699,
        widget=StringWidget(
            label="Border",
            description="Color for the border around the search results",
            label_msgid='googlecoop_label_borderColor',
            description_msgid='googlecoop_help_borderColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='titleColor',
        default="0000CC",
        widget=StringWidget(
            label="Title",
            description="Color for the search result Title",
            label_msgid='googlecoop_label_titleColor',
            description_msgid='googlecoop_help_titleColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='backgroundColor',
        default="FFFFFF",
        widget=StringWidget(
            label="Background",
            description="Background Color",
            label_msgid='googlecoop_label_backgroundColor',
            description_msgid='googlecoop_help_backgroundColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='textColor',
        default=0,
        widget=StringWidget(
            label="Text",
            description="Color of the result description",
            label_msgid='googlecoop_label_textColor',
            description_msgid='googlecoop_help_textColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='linkColor',
        default=8000,
        widget=StringWidget(
            label="Links",
            description="Color for the URL",
            label_msgid='googlecoop_label_linkColor',
            description_msgid='googlecoop_help_linkColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='visitedColor',
        default=663399,
        widget=StringWidget(
            label="Visited Links",
            description="Color for visited URLs",
            label_msgid='googlecoop_label_visitedColor',
            description_msgid='googlecoop_help_visitedColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

    StringField(
        name='cachedColor',
        default=0,
        widget=StringWidget(
            label="Cached Link",
            description="Color for cached links",
            label_msgid='googlecoop_label_cachedColor',
            description_msgid='googlecoop_help_cachedColor',
            i18n_domain='googlecoop',
        ),
        read_permission="View",
        write_permission="Manage Portal"
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

googlecoop_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class googlecoop(UniqueObject, BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UniqueObject,'__implements__',()),) + \
        (getattr(BaseContent,'__implements__',()),)

    meta_type = 'googlecoop'
    suppl_views = ()
    typeDescription = "Google Coop"
    typeDescMsgId = 'description_edit_googlecoop'
    toolicon = 'google-coop.png'

    _at_rename_after_creation = True

    schema = googlecoop_schema

    ##code-section class-header #fill in your manual code here
    def getAdsVocabulary(self):
    	return ADPLACEMENT.items()

    def getAddStatusVocabulary(self):
        return ADDSTATUS.items()
    ##/code-section class-header


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        BaseContent.__init__(self,'portal_googlecoop')
        self.setTitle('Google Coop')
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()
        
        ##code-section post-edit-method-footer #fill in your manual code here
        ##/code-section post-edit-method-footer


    # Methods

    security.declarePublic('getGoCoopJS')
    def getGoCoopJS(self):
        """
        Return JS code to display your search results
        """
	JSCode ='''
  	var googleSearchIframeName = "results_%s";
  	var googleSearchFormName = "searchbox_%s";
  	var googleSearchFrameWidth = 600;
  	var googleSearchFrameborder = 0;
  	var googleSearchDomain = "%s";
  	var googleSearchPath = "/cse";
	'''  % (self.identifier, self.identifier, self.domain)

	return JSCode

    security.declarePublic('getAllRemoteURLs')
    def getAllRemoteURLs(self):
        """
        Returns all remote_urls from the portal catalog
        """
        URLs = self.portal_catalog.uniqueValuesFor('getRemoteUrl')
        AllURLs = '\n'.join(URLs)
        return AllURLs

    security.declarePublic('uniqueURLID')
    def uniqueURLID(self,URL=None):
        """
        Return an uniqe ID for a given URL
        """
        try:
            sig = md5.new(URL)
        except:
            sig = md5.new(self.identifier)
        urlId = "_cse_" + sig.hexdigest()
        return urlId

    security.declarePublic('getCseCrefJS')
    def getCseCrefJS(self):
        """
        Return JavaScript for a Linked Custom Search Engine
        """
        JSCode ='''
          var googleSearchIframeName = "results_cref";
          var googleSearchFormName = "searchbox_cref";
          var googleSearchFrameWidth = 600;
          var googleSearchFrameborder = 0;
          var googleSearchDomain = "%s";
          var googleSearchPath = "/cse";
        '''  % (self.domain)
        return JSCode

    security.declarePublic('subject2label')
    def subject2label(self,Keyword=None):
        """
        Convert a plone subject into a google label.
        Labels seem to have to constist solely lowercase letters and _ underscores
        """
        if Keyword:
           plone_tool = getToolByName(self, 'plone_utils', None)
           if plone_tool is None or not shasattr(plone_tool, 'normalizeString'):
                return KeyWord
           else:
                label=plone_tool.normalizeString(Keyword)
                label=label.replace('-','_')
                return label

    # Manually created methods

    def getAdsVocabulary(self):
    	return ADPLACEMENT.items()

    def getAddStatusVocabulary(self):
        return ADDSTATUS.items()
    ##/code-section class-header


registerType(googlecoop, PROJECTNAME)
# end of class googlecoop

##code-section module-footer #fill in your manual code here
##/code-section module-footer



