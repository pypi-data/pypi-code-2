from archetypes.schemaextender.interfaces import ISchemaModifier, IBrowserLayerAwareExtender
from Products.Archetypes.atapi import *
from zope.interface import implements, Interface
from zope.component import adapts, provideAdapter

from Products.FacultyStaffDirectory.interfaces.person import IPerson
from collective.fsdsimplifier.browser.interfaces import IFsdSimplifierLayer

class PersonModifier(object):
    """Hide fields that tend to clutter up the interface and confuse users"""

    adapts(IPerson)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IFsdSimplifierLayer

    def __init__(self, context):
        self.context = context

    def fiddle(object, schema):
        """Hide fields that tend to clutter up the interface and confuse users"""

        # Hide unwanted schema fields that clutter up the space             
        for hideme in ['Employment Information','User Settings', 'categorization', 'dates', 'ownership', 'settings']:
            for field in schema.getSchemataFields(hideme):
                new_field = schema[field.getName()].copy()
                new_field.write_permission="FacultyStaffDirectory: Change Person IDs"
                schema[field.getName()] = new_field
			    
        return schema

