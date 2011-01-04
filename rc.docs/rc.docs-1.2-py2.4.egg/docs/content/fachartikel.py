"""Definition of the Fachartikel content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from rc.docs import docsMessageFactory as _
from rc.docs.interfaces import IFachartikel
from rc.docs.config import PROJECTNAME

FachartikelSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        'untertitel',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Untertitel"),
            description=_(u"Untertitel des Fachartikels."),
            size = 50,
        ),
        required=False,
    ),

    atapi.TextField(
        'aboutauthors',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Zu den Autoren"),
            description=_(u"Zus&auml;tzliche Angaben &uuml;ber die Autoren."),
            rows = 15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),


    atapi.TextField(
        'fabstract',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Abstract"),
            description=_(u"Eine kurze Beschreibung."),
            rows = 15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),

    atapi.TextField(
        'fachartikeltext',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Fachartikel"),
            description=_(u"Fachartikel erfassen."),
            rows = 15,
        ),
        default_output_type='text/x-html-safe',
        searchable=1,
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

FachartikelSchema['title'].storage = atapi.AnnotationStorage()
FachartikelSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(FachartikelSchema, moveDiscussion=False)

# Hide the 'description' field
FachartikelSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class Fachartikel(base.ATCTContent):
    """Description of the Example Type"""
    implements(IFachartikel)

    meta_type = "Fachartikel"
    schema = FachartikelSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    untertitel = atapi.ATFieldProperty('untertitel')
    aboutauthors = atapi.ATFieldProperty('aboutauthors')
    fabstract = atapi.ATFieldProperty('fabstract')
    fachartikeltext = atapi.ATFieldProperty('fachartikeltext')

atapi.registerType(Fachartikel, PROJECTNAME)
