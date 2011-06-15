# -*- coding: utf-8 -*-

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from Products.CMFCore.utils import getToolByName
from Products.JYUDynaPage.interfaces import IDynaPage, IUpdatePaths
from Products.JYUDynaPage.config import PROJECTNAME
from Products.JYUDynaPage.content.schemata import DynaPageSchema

from zope.interface import implements

class DynaPage(OrderedBaseFolder):
    """A simple folderish page -like archetype containing dynamic lists
    """
   
    implements(IDynaPage, IUpdatePaths) #, INonStructuralFolder)
    
    portal_type                 = "DynaPage"
    schema                      = DynaPageSchema
    _at_rename_after_creation   = True
    
    text = ATFieldProperty('text')
    inheritImage = ATFieldProperty('inheritImage')

    # First list
    first_list_active = ATFieldProperty('first_list_active')
    first_list_style = ATFieldProperty('first_list_style')
    first_list_position = ATFieldProperty('first_list_position')
    first_list_title = ATFieldProperty('first_list_title')
    first_list_order = ATFieldProperty('first_list_order')
    first_list_order_by = ATFieldProperty('first_list_order_by')
    first_list_types = ATFieldProperty('first_list_types')
    first_list_state = ATFieldProperty('first_list_state')
    first_list_custom_view_fields = ATFieldProperty('first_list_custom_view_fields')
    first_list_keywords = ATFieldProperty('first_list_keywords')
    first_list_items = ATFieldProperty('first_list_items')
    first_list_path = ATFieldProperty('first_list_path')
    first_list_rss_title = ATFieldProperty('first_list_rss_title')
    
    # Second list
    second_list_active = ATFieldProperty('second_list_active')
    second_list_style = ATFieldProperty('second_list_style')
    second_list_position = ATFieldProperty('second_list_position')
    second_list_title = ATFieldProperty('second_list_title')
    second_list_order = ATFieldProperty('second_list_order')
    second_list_order_by = ATFieldProperty('second_list_order_by')
    second_list_types = ATFieldProperty('second_list_types')
    second_list_state = ATFieldProperty('second_list_state')
    second_list_custom_view_fields = ATFieldProperty('second_list_custom_view_fields')
    second_list_keywords = ATFieldProperty('second_list_keywords')
    second_list_items = ATFieldProperty('second_list_items')
    second_list_path = ATFieldProperty('second_list_path')
    
    # Third list
    third_list_active = ATFieldProperty('third_list_active')
    third_list_style = ATFieldProperty('third_list_style')
    third_list_position = ATFieldProperty('third_list_position')
    third_list_title = ATFieldProperty('third_list_title')
    third_list_order = ATFieldProperty('third_list_order')
    third_list_order_by = ATFieldProperty('third_list_order_by')
    third_list_types = ATFieldProperty('third_list_types')
    third_list_state = ATFieldProperty('third_list_state')
    third_list_custom_view_fields = ATFieldProperty('third_list_custom_view_fields')
    third_list_keywords = ATFieldProperty('third_list_keywords')
    third_list_items = ATFieldProperty('third_list_items')
    third_list_path = ATFieldProperty('third_list_path')
    
    # Fourth list
    fourth_list_active = ATFieldProperty('fourth_list_active')
    fourth_list_style = ATFieldProperty('fourth_list_style')
    fourth_list_position = ATFieldProperty('fourth_list_position')
    fourth_list_title = ATFieldProperty('fourth_list_title')
    fourth_list_order = ATFieldProperty('fourth_list_order')
    fourth_list_order_by = ATFieldProperty('fourth_list_order_by')
    fourth_list_types = ATFieldProperty('fourth_list_types')
    fourth_list_state = ATFieldProperty('fourth_list_state')
    fourth_list_custom_view_fields = ATFieldProperty('fourth_list_custom_view_fields')
    fourth_list_keywords = ATFieldProperty('fourth_list_keywords')
    fourth_list_items = ATFieldProperty('fourth_list_items')
    fourth_list_path = ATFieldProperty('fourth_list_path')


#    def getContentTypes(self):
#        """ return a list of user addable content types """ 
#        pu          = getToolByName(self, 'plone_utils')
#        userTypes   = pu.getUserFriendlyTypes()
#
#        return userTypes

    def getSubjects(self):
        pc = getToolByName(self, 'portal_catalog')
        return pc.uniqueValuesFor('Subject')

    # Copied from ATTopic
    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from portal_catalog."""
        tool = getToolByName(self, 'portal_atct')
        return tool.getMetadataDisplay(exclude) 

    def getParentPathURL(self):
        """Return a parent."""
        return self.aq_parent.absolute_path()
    
registerType(DynaPage, PROJECTNAME)
