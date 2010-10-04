from Products.CMFCore.utils import getToolByName
from plone.memoize import ram

from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi

class RSVPStringField(ExtensionField, atapi.StringField):
    pass

class RSVPSelectionField(ExtensionField, atapi.StringField):
    
    @ram.cache(lambda func, self, content_instance, sobject_type: (content_instance.portal_url(), sobject_type))
    def _get_fields(self, content_instance, sfobject_type):
        sbc = getToolByName(content_instance, 'portal_salesforcebaseconnector')
        return sbc.describeSObjects(sfobject_type)[0]
    
    def Vocabulary(self, content_instance):
        """Populate the vocabulary options with the available
           fields for the configured Salesforce.com object type
           or failing that the default of the 'Campaign' object.
        """
        curr_sfobject_type = content_instance.getField('sfObjectSignupType').get(content_instance) or 'Campaign'
        obj_schema = self._get_fields(content_instance, curr_sfobject_type)
        
        # construct a display list
        fieldDisplay = atapi.DisplayList()
        fieldDisplay.add('', '')
        for k,v in obj_schema.fields.items():
            fieldDisplay.add(k, '%s (%s)' % (v.label, v.name))
        return fieldDisplay
    

class RSVPReferenceField(ExtensionField, atapi.ReferenceField):
    pass


class RSVPObjTypeField(ExtensionField, atapi.StringField):
    
    @ram.cache(lambda func, self, content_instance: content_instance.portal_url())
    def Vocabulary(self, content_instance):
        """Populate the vocabulary options with the available
           objects for the configured Salesforce.com instance.
        """
        # get base connector
        sbc = getToolByName(content_instance, 'portal_salesforcebaseconnector')
        
        # get the eligible types
        types = sbc.describeGlobal()['types']
        typesDisplay = atapi.DisplayList()
        for t in types:
            typesDisplay.add(t, t)
        return typesDisplay
