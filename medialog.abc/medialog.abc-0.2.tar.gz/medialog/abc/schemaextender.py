from zope.interface import implements
from zope.component import adapts
# This Python file uses the following encoding: utf-8
import os, sys

from zope.i18nmessageid import MessageFactory

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender, IOrderableSchemaExtender   
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes.atapi import *
from Products.ATContentTypes.interface import IATImage

from interfaces import IAbcLayer

# Any field you tack on must have ExtensionField as its first subclass:
class _BooleanExtensionField (ExtensionField, BooleanField): 
    pass


class ContentTypeExtender(object):
    """Adapter that adds custom settings."""
    adapts(IATImage)
    implements(ISchemaExtender, IBrowserLayerAwareExtender, IOrderableSchemaExtender)
    layer = IAbcLayer
    _fields = [
        _BooleanExtensionField('smaa',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Smaa kort",
            )
        ),       

        _BooleanExtensionField('medium',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Medium kort",
            )
        ),
        
        _BooleanExtensionField('store',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Store kort",
            )
        ),
   
   
        _BooleanExtensionField('bordkort',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Bordkort",
            )
        ),  
        
        _BooleanExtensionField('invitasjonskort',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Invitasjonskort",
            )
        ),  
 
        _BooleanExtensionField('takkekort',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Takekort",
            )
        ),  

        _BooleanExtensionField('hoye',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Hoye blomsterkort",
            )
        ),

        _BooleanExtensionField('stickers',
        required=False,
        schemata = "settings",
        searchable=True,
        widget = BooleanWidget(
            label=u"Party Stickers",
            )
        ),    
        
    ]
    
    
    def __init__(self, context):
    	self.context = context
    	
    def getOrder(self, schematas):
        """ Manipulate the order in which fields appear.
        @param schematas: Dictonary of schemata name -> field lists

        @return: Dictionary of reordered field lists per schemata.
                """
        schematas["abc"] = ['smaa', 'medium', 'store', 'bordkort', 'invitasjonskort', 'takkekort', 'hoye', 'stickers']

        return schematas

    def getFields(self):
        return self._fields

#    def __init__(self, contentType):
#        pass    