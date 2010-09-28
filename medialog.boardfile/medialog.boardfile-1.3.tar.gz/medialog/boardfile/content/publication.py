"""Definition of the Publication content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.interface.file import IATFile
 
from medialog.boardfile import boardfileMessageFactory as _
from medialog.boardfile.interfaces import IPublication
from medialog.boardfile.config import PROJECTNAME


from Products.validation.validators.RangeValidator import RangeValidator

from Products.validation import validation
validYear = RangeValidator("validYear", 2010, 2050)
validation.register(validYear)
 
PublicationSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.FileField(
        'file',
        storage=atapi.AnnotationStorage(),
        widget=atapi.FileWidget(
            label=_(u"File"),
            description=_(u".doc, .pdf or .zip file to upload"),
        ),
        required=True,
    ),


    atapi.StringField(
        'publicationtitle',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Publication Title"),
            description=_(u"Publication Title as it appears in the Journal"),
        ),
        required=True,
        searchable=True,
    ),

    atapi.LinesField(
        'authorlist',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Authorlist"),
            description=_(u"List of publication authors"),
        ),
        required=True,
        searchable=True,
    ),

    atapi.StringField(
        'wp',
        searchable = True,
		required = True,
		default = "",
		vocabulary = [('Please Choose', 'Not set'), ('WP1', 'WP1'), ('WP2', 'WP2'), ('WP3', 'WP3'), ('WP4', 'WP4'), ('WP5', 'WP5'), ('WP6', 'WP6')],
		type = """lines""",
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            format='select',
            label=_(u"Select WP"),            
            description=_(u"The Work Package of the publication."),          
        ),
        validators=("isUnixLikeName"),
    ),
  
  
    atapi.IntegerField(
        'publishingyear',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Year"),
            description=_(u"Year Published"),
        ),
        validators=("isInt", "validYear"),
        required = True,
    ),

    
))


# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PublicationSchema['title'].storage = atapi.AnnotationStorage()
PublicationSchema['title'].widget.label = 'Journal - Conference - Report - Thesis'
PublicationSchema['title'].required = True
PublicationSchema['description'].storage = atapi.AnnotationStorage()
PublicationSchema['description'].widget.label = 'Abstract'
PublicationSchema['description'].required = False

schemata.finalizeATCTSchema(PublicationSchema, moveDiscussion=False)

class Publication(base.ATCTContent):
    """Publication content type"""
    implements(IATFile)

    meta_type = "Publication"
    schema = PublicationSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    publicationtitle = atapi.ATFieldProperty('publicationtitle')

    authorlist = atapi.ATFieldProperty('authorlist')
    
    file = atapi.ATFieldProperty('file')

    wp = atapi.ATFieldProperty('wp')

    publishingyear = atapi.ATFieldProperty('publishingyear')
    
atapi.registerType(Publication, PROJECTNAME)
