"""Definition of the SalesforceGenericObject content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from datetime import date, datetime, timedelta

# -*- Message Factory Imported Here -*-

from collective.salesforce.query.interfaces import ISalesforceGenericObject
from collective.salesforce.query.config import PROJECTNAME

SalesforceGenericObjectSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

SalesforceGenericObjectSchema['title'].storage = atapi.AnnotationStorage()
SalesforceGenericObjectSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SalesforceGenericObjectSchema, moveDiscussion=False)

RAISERRORFIELDS = ['getRawRelatedItems']


class SalesforceGenericObject(base.ATCTContent):
    """A Generic Placeholder to represent a Salesforce Item"""
    implements(ISalesforceGenericObject)

    meta_type = "SalesforceGenericObject"
    schema = SalesforceGenericObjectSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def __init__(self, *args, **kwargs):
        super(SalesforceGenericObject, self).__init__(*args, **kwargs)
        self._inner_data={}
        self.__parent__ = None
        self._searchable_text = []

    def __getattribute__ (self, attr):
        """
        We want to catch all calls to getattribute to interpose the content from
        our salesforce data when SalesforceQueryIndex_ is the prefix of an attr
        """
        if attr.startswith("SalesforceQueryIndex_"):
            data_index = attr[21:]
            if data_index not in object.__getattribute__(self,'__parent__').searchable_fields:
                raise AttributeError(attr)
            value = object.__getattribute__(self, '_inner_data').get(data_index, '')
            if isinstance(value,(str,unicode,bool)):
                value = value.lower()
            elif isinstance(value,(date,datetime)):
                value = value.isoformat()
            elif value is None:
                value = ''
            else:
                value = repr(value)
            return value
        if attr in RAISERRORFIELDS:
            #Better to not try to emulate those
            raise AttributeError(attr)
        return  base.ATCTContent.__getattribute__(self, attr)

    def setSalesforceData(self, data, searchable_fields):
        """
        Store the data from salesforce in an internal attribute
        """
        self._inner_data = data
        searchable_text = []
        for key in searchable_fields:
            if isinstance(self._inner_data.get(key, ''), str):
                searchable_text += self._inner_data.get(key, '').lower().split()
        self._searchable_text = searchable_text

    def setParent(self, parent):
        """
        This is no real object so we want to hold a reference to the parent
        salesforcequery for the index moment.
        """
        self.__parent__ = parent
        self.aq_parent = parent

    def getPhysicalPath(self):
        """
        We fake the physical path contatenating the parent with an identifiable part
        """
        return self.__parent__.getPhysicalPath() + ("salesforce_item_%s" % self.id,)

    def absolute_url(self):
        """
        The url points to the parent's url that shows this object details.
        """
        return "%s/salesforcedetails_view?item_id=%s" % (self.__parent__.absolute_url(), self.id)

    def acl_users(self):
        return self.__parent__.acl_users

    def SearchableText(self):
        """
        In case we need to be searchable we combine the content of the chosen indexes.
        """
        return self._searchable_text
 

atapi.registerType(SalesforceGenericObject, PROJECTNAME)
