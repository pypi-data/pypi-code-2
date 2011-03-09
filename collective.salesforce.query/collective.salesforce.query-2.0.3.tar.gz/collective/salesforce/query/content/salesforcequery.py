"""Definition of the SalesforceQuery content type
"""
import zope.component

from zope.interface import implements, directlyProvides
from zLOG import LOG, INFO

from ZPublisher.HTTPRequest import HTTPRequest
from zExceptions import Redirect

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions as CMFCorePermissions

from Products.Archetypes.interfaces import IObjectInitializedEvent
from zope.lifecycleevent import IObjectCreatedEvent 

from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from collective.salesforce.query import queryMessageFactory as _
from collective.salesforce.query.interfaces import ISalesforceQuery
from collective.salesforce.query.content.salesforcegenericobject import SalesforceGenericObject
from collective.salesforce.query.widgets import InAndOutOrderableWidget
from collective.salesforce.query.config import PROJECTNAME

# dummy class used with manage_addIndex
# Thanks to Mikko Ohtamaa http://plone.org/documentation/kb/adding-new-fields-to-smart-folders-search
class args:
    def __init__(self, **kw):
        self.__dict__.update(kw)
    def keys(self):
        return self.__dict__.keys()


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

    atapi.StringField(
        'titlefield',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Title Field"),
            description=_(u"Select a field from salesforce to be presented as title, this will be effective after a full update."),
        ),
        required=False,
        vocabulary='getSFFieldsVocabulary',
    ),

    atapi.StringField(
        'descriptionfield',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Description Field"),
            description=_(u"Select a field from salesforce to be presented as description, this will be effective after a full update"),
        ),
        required=False,
        vocabulary='getSFFieldsVocabulary',
    ),

    
    atapi.LinesField(
        'listing_visible_fields',
        storage=atapi.AnnotationStorage(),
        widget=InAndOutOrderableWidget(
            label=_(u"Listing fields"),
            description=_(u"Choose fields to show on listings for each SalesForce item. Until data type from Salesforce is not choosen (and item saved) you can't setup this field. Save first when creating."),
        ),
        required=False,
        multiValued=True,
        vocabulary='getSFFieldsVocabulary',
    ),

    atapi.LinesField(
        'details_visible_fields',
        storage=atapi.AnnotationStorage(),
        widget=InAndOutOrderableWidget(
            label=_(u"Detail fields"),
            description=_(u"Choose fields to show on details view for each SalesForce item. Until data type from Salesforce is not choosen (and item saved) you can't setup this field. Save first when creating."),
        ),
        required=False,
        multiValued=True,
        vocabulary='getSFFieldsVocabulary',
    ),

    atapi.LinesField(
        'searchable_fields',
        storage=atapi.AnnotationStorage(),
        widget=InAndOutOrderableWidget(
            label=_(u"Fields indexed for search"),
            description=_(u"Choose fields to be indexed. You will be allowed to perform search on these indexes , \
                beware, too many of these might bloath your site, use only the necessary ones. Until data type from Salesforce is not choosen (and item saved) you can't setup this field. Save first when creating."),
        ),
        required=False,
        multiValued=True,
        vocabulary='getSFFieldsVocabulary',
    ),


    ))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

SalesforceQuerySchema['title'].storage = atapi.AnnotationStorage()
SalesforceQuerySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SalesforceQuerySchema, moveDiscussion=False)

#def add_catalog_to_sfquery(obj, event):
#    LOG('collectiv.salesforce.query', INFO,
#        'calling add catalog with obj id: %d', obj.getId())
#    if not hasattr(obj, 'portal_faceted'):
#        obj.manage_addProduct['ZCatalog'].manage_addZCatalog(id='portal_faceted',
#                                                             title='Catalog')
def add_catalog_to_sfquery(obj, event):
    if not hasattr(obj, 'own_catalog'):
        obj.manage_addProduct['ZCatalog'].manage_addZCatalog(id='own_catalog',
                                                             title='Catalog')


class SalesforceQuery(base.ATCTFolder):
    """A page showing content from Salesforce"""
    implements(ISalesforceQuery)

    meta_type = "SalesforceQuery"
    schema = SalesforceQuerySchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    datatype = atapi.ATFieldProperty('datatype')
    titlefield = atapi.ATFieldProperty('titlefield')
    descriptionfield = atapi.ATFieldProperty('descriptionfield')
    listing_visible_fields = atapi.ATFieldProperty('listing_visible_fields')
    details_visible_fields = atapi.ATFieldProperty('details_visible_fields')
    searchable_fields = atapi.ATFieldProperty('searchable_fields')

    def __init__(self,*args,**kwargs):
        super(SalesforceQuery,self).__init__(*args,**kwargs)
        self._fs_data = PersistentMapping()

    def get_catalogs(self):
        local_catalog = self.get_local_catalog()
        site_wide_catalog = getToolByName(self, 'portal_catalog')
        return (local_catalog, site_wide_catalog)

    def get_local_catalog(self):
        obj_id = "portal_sfq_catalog"
        catalog = getattr(self, obj_id, None)
        if catalog:
            return catalog
        else:
            raise AttributeError("No local catalog")


    #--------------------Mutators
    security.declareProtected(CMFCorePermissions.View,'setSearchable_fields')
    def setSearchable_fields(self, value, field=None):
        if value != self.searchable_fields:
            delta_out = set(self.searchable_fields).difference(set(value))
            delta_in = set(value).difference(set(self.searchable_fields))
            self.update_indexes(delta_out, delta_in)
            self.searchable_fields = value
            self.clean_catalog_before_data()
            self.recatalog()

    def setDatatype(self, value, field=None):
        changed = False
        if self.datatype != value:
            changed = True
        self.datatype = value
        if changed:
            self.clean_catalog_before_data()
            self._fs_data = PersistentMapping()
        self.datatype = value


    #--------------------Utils


    def _queryAll(self, query):
        """Construct a resultset with all resulst from salesforce, regardles of the batch limit, data queries should
        always be done with this"""
        salesforce_tool = self._get_sf_tool()
        partial = salesforce_tool.query(query)
        results = [a_partial for a_partial in partial['records']]
        while partial['done'] == False:
            partial = salesforce_tool.queryMore(partial['queryLocator'])
            results += [a_partial for a_partial in partial['records']]
        return {'records':results}

    security.declarePrivate('purge_cache')
    def purge_cache(self):
        """ Revert the cache of objects to its initial state"""
        self._fs_data = PersistentMapping()

    security.declarePrivate('update_indexes')
    def update_indexes(self, delta_out, delta_in):
        """
        Update Catalog indexes when indexed fields change
        """
        
        catalog_tool = self.get_local_catalog()
        portal_catalog = getToolByName(self, 'portal_catalog')
        existing_indexes = [cat_index.getId() for cat_index in catalog_tool.index_objects()]
        for removable in delta_out:
            formatted_removable = "SalesforceQueryIndex_%s" % removable
            if (formatted_removable in existing_indexes) and \
                    (len(portal_catalog({'portal_type':'SalesforceQuery', 'Indexable Fields':removable}))==1) :
                #We only remove the index if no other query uses it
                catalog_tool._removeIndex(formatted_removable)

        extra = args(doc_attr='SearchableText',
                     lexicon_id='plone_lexicon',
                     index_type='Okapi BM25 Rank')

        for addable in [index for index in delta_in if index]: #set can return a set with ['']
            formatted_addable = "SalesforceQueryIndex_%s" % addable
            if formatted_addable not in existing_indexes:
                catalog_tool.manage_addIndex(formatted_addable, "FieldIndex", extra)
                #TODO: add magic to find out when this applies?
                #catalog_tool.manage_addIndex("getAvailability", "DateIndex",extra)
        self.reindexObject()

    security.declarePrivate('clean_catalog_before_data')
    def clean_catalog_before_data(self, data={}):
        return
        new_data = data and data or self._fs_data
        catalogs = self.get_catalogs()
        path = "/".join(self.getPhysicalPath())
        for item in new_data.keys():
            for catalog in catalogs:
                catalog.uncatalog_object("%s/salesforce_item_%s" % (path, item))


    security.declarePrivate('recatalog')
    def recatalog(self, data={}):
        catalogs = self.get_catalogs()
        membership = getToolByName(self, 'portal_membership')
        member = membership.getAuthenticatedMember()
        new_data = data and data or self._fs_data
        for key, value in new_data.iteritems():
            indexable = SalesforceGenericObject(key)
            description = value.get('Description', value.get('description', ''))
            if self.descriptionfield:
                description = value.get(self.descriptionfield, description)
            indexable.description = description 
            title = key
            if self.titlefield:
                title = value.get(self.titlefield, title)
            indexable.title = title
            indexable.setSalesforceData(value, self.searchable_fields)
            indexable.setParent(self)
            roles = list(indexable.get_local_roles_for_userid(member.id))
            member_id = member.id and member.id or 'admin' #failsafe
            if 'Owner' not in roles:
                roles.append('Owner')
                indexable.manage_setLocalRoles(member_id, roles)
            indexable.reindexObject()
            for catalog in catalogs:
                catalog.catalog_object(indexable)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,'update')
    def update(self,REQUEST=None,RESPONSE=None):
        """updates item data"""
        headers = [k for k,v in self.getSFFields(update=True)]
        salesforce_tool =  self._get_sf_tool() 
        query = "SELECT %(headers)s FROM %(datatype)s" % {'headers':",".join(headers),'datatype':self.datatype}
        results = self._queryAll(query)

        data = PersistentMapping()
        for item in results['records']:
            if isinstance(item,dict):
                item = PersistentMapping(item)
            if item.get('Id',None) is None:
                continue
            data[item['Id']] = item
        self.clean_catalog_before_data()
        self._fs_data = data
        self.recatalog()

        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url())


    security.declareProtected(CMFCorePermissions.View,'getSFFields')
    def getSFFields(self,update=False):
        """
        get all fields from the given data type
        """
        if not self.datatype:
            return []
        if not update and hasattr(self,'_headers'):
            return self._headers
        else:
            salesforce_tool = self._get_sf_tool()
            result = salesforce_tool.describeSObjects([self.datatype,])[0]
            headers = []
            for field_key,field_data in result.__dict__['fields'].items():
                headers.append((field_key,field_data))
            headers.sort(key=lambda x: x[1].label)
            self._headers = PersistentList(headers)
            return list(self._headers)

    security.declareProtected(CMFCorePermissions.View,'getSFFieldsVocabulary')
    def getSFFieldsVocabulary(self):
        """returns vocabulary of fields"""
        return atapi.DisplayList([(k,v.label) for k,v in self.getSFFields()])

    security.declareProtected(CMFCorePermissions.View,'getSFFieldsVocabularyEmpty')
    def getSFFieldsVocabularyEmpty(self):
        """returns vocabulary of fields"""
        return atapi.DisplayList([('','')]+[(k,v.label) for k,v in self.getSFFields()])

    security.declareProtected(CMFCorePermissions.View,'getHeaders')
    def getHeaders(self,details=False):
        """
        get only visible fields from the given data type
        """
        fields = dict(self.getSFFields())
        if details:
            headers = [(k,fields[k]) for k in self.details_visible_fields if k in fields]
        else:
            headers = [(k,fields[k]) for k in self.listing_visible_fields if k in fields]
        if not headers:
            headers = fields.items()
        return headers

    def _get_sf_tool(self):
        return getToolByName(self, 'portal_salesforcebaseconnector')

    security.declarePrivate('data')
    def data(self):
        return self._fs_data

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to SalesforceGenericObjects
        """
        if name.startswith('salesforce_item_'):
            if not isinstance(REQUEST,HTTPRequest):
                # this is a call form reindexObjectSecurity
                return None # Making use of a BBB hack
            key = name[16:]
            if key in self._fs_data.keys():
                raise Redirect("%s/salesforcedetails_view?item_id=%s" % (self.absolute_url(), key))

        return base.ATCTFolder.__bobo_traverse__(self, REQUEST, name)

atapi.registerType(SalesforceQuery, PROJECTNAME)
