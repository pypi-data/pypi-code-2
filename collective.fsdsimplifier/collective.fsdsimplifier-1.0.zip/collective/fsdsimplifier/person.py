from archetypes.schemaextender.interfaces import ISchemaModifier, IBrowserLayerAwareExtender
from Products.Archetypes.atapi import *
from zope.interface import implements, Interface
from zope.component import adapts, provideAdapter

from Products.FacultyStaffDirectory.interfaces.person import IPerson
from collective.fsdsimplifier.browser.interfaces import IThemeSpecific

class PersonModifier(object):
    """Hide fields that tend to clutter up the interface and confuse users"""

    adapts(IPerson)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IThemeSpecific

    def __init__(self, context):
        self.context = context

    def fiddle(object, schema):
        """Hide fields that tend to clutter up the interface and confuse users"""

        # Hide unwanted schema that clutter up the space             
        for hideme in ['User Settings', 'categorization', 'dates', 'ownership', 'settings']:
            for fieldName in schema.getSchemataFields(hideme):
                fieldName.write_permission="FacultyStaffDirectory: Change Person IDs"
			    
        return schema

