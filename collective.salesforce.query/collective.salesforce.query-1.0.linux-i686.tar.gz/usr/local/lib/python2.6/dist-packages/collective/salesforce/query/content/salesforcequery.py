"""Definition of the SalesforceQuery content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from collective.salesforce.query import queryMessageFactory as _
from collective.salesforce.query.interfaces import ISalesforceQuery
from collective.salesforce.query.config import PROJECTNAME

SalesforceQuerySchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'datatype',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Data Type"),
            description=_(u"Select data type from Salesforce"),
        ),
        required=True,
        vocabulary_factory='salesforce.datatypes',
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

SalesforceQuerySchema['title'].storage = atapi.AnnotationStorage()
SalesforceQuerySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SalesforceQuerySchema, moveDiscussion=False)

class SalesforceQuery(base.ATCTContent):
    """A page showing content from Salesforce"""
    implements(ISalesforceQuery)

    meta_type = "SalesforceQuery"
    schema = SalesforceQuerySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    datatype = atapi.ATFieldProperty('datatype')


atapi.registerType(SalesforceQuery, PROJECTNAME)
