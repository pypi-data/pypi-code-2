from zope.interface import implements
from zope.component import adapts
from zope.i18nmessageid import MessageFactory

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.atapi import *
from Products.ATContentTypes.interface import IATFolder
#from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
#from zope.component import getUtility 


_ = MessageFactory('medialog.foldersubskins')


# Any field you tack on must have ExtensionField as its first subclass:
class _LinesExtensionField(ExtensionField, StringField):
    pass


class ContentTypeExtender(object):
    """Adapter that adds custom css settings."""
    adapts(IATFolder)

    implements(ISchemaExtender)
    _fields = [
        _LinesExtensionField('extracss',
        required=False,
        schemata = "settings",
        searchable=False,
        widget = LinesWidget(
            label=u"Extra css",
            description=u"The name of a css file that will work for everything in this folder.",            
            )
        )
    ]
    
    
    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields

#    def __init__(self, contentType):
#        pass    