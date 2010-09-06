""" Definition of the WoW Character content type """

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from collective.wowcharacter import wowcharacterMessageFactory as _
from collective.wowcharacter.interfaces import IWoWCharacter
from collective.wowcharacter.config import PROJECTNAME

WoWCharacterSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    # author: marc goetz

     atapi.StringField(
         name="name",
         widget=atapi.StringWidget(
             label=u"Name",
             label_msgid="collectivewowcharacter_label_name",
             il8n_domain="collectivewowcharacter",
             maxlength=25,
             size=25,
             ),

             required=True,
             searchable=True
             ),

     atapi.StringField(
         name="realm",
         widget=atapi.StringWidget(
             label=u"Realm",
             label_msgid="collectivewowcharacter_label_realm",
             il8n_domain="collectivewowcharacter",
             maxlength=25,
             size=25,
             ),

             required=True,
             searchable=True
             ),

      atapi.StringField(
         name="faction",
         vocabulary=[("Alliance","Alliace"),("Horde","Horde")],
         widget=atapi.SelectionWidget(
             format="select",
             label=u"Faction",
             label_msgid="collectivewowcharacter_label_faction",
             il8n_domain="collectivewowcharacter",
             ),

             required=True,
             searchable=True
             ),

      atapi.StringField(
         name="zone",
         vocabulary=[("EU","EU"),("US","US")],
         widget=atapi.SelectionWidget(
             format="select",
             label=u"Zone",
             label_msgid="collectivewowcharacter_label_zone",
             il8n_domain="collectivewowcharacter",
             ),

             required=True,
             searchable=True
             ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

WoWCharacterSchema['title'].storage = atapi.AnnotationStorage()
WoWCharacterSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(WoWCharacterSchema, moveDiscussion=False)

class WoWCharacter(base.ATCTContent):
    """An installable content type for WoW characters"""
    implements(IWoWCharacter)

    meta_type = "WoW Character"
    schema = WoWCharacterSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(WoWCharacter, PROJECTNAME)
