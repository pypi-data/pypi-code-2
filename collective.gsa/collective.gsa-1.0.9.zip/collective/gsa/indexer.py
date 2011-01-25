from logging import getLogger
from socket import error
import re
from persistent import Persistent

from ZODB.POSException import ConflictError

from zope.interface import implements
from zope.component import queryUtility, queryMultiAdapter

from plone.app.content.interfaces import IIndexableObjectWrapper

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex

from collective.gsa.interfaces import IGSAIndexQueueProcessor
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.interfaces import IContentProvider
from collective.gsa.utils import safe_unicode
from collective.gsa.gsa import GSAException

logger = getLogger('collective.gsa.indexer')
BADCHAR_PATTERN = re.compile('[\x00-\x08\x11\x12\x14-\x19]')


def indexable(obj):
    """ indicate whether a given object should be indexed; for now only
        objects inheriting one of the catalog mixin classes are considerd """
    return isinstance(obj, CatalogMultiplex) or isinstance(obj, CMFCatalogAware)


class GSAIndexQueueProcessor(Persistent):
    """ a queue processor for gsa """
    implements(IGSAIndexQueueProcessor)

    def __init__(self, manager=None):
        self.manager = manager      # for testing purposes only
        self.straight = False
        
    def index(self, obj, attributes=None):
        conn = self.getConnection()
        if conn is not None and indexable(obj):
            # prepare data
            data = self.prepareData(obj)
            if data is None:
                return
            # send
            try:
                logger.debug('indexing %r (%r)', obj, data)
                conn.add(self.straight, **data)
                data = None
            except (GSAException, error):
                logger.exception('exception during indexing %r', obj)
                
                
    def reindex(self, obj, attributes=None):
        self.index(obj, attributes)
        
    def unindex(self, obj):
        conn = self.getConnection()
        if conn is not None:
            data = {}
            data['url'] = obj.absolute_url()
            data['path'] = obj.absolute_url_path()
            try:
                logger.debug('unindexing %r (%r)', obj, data)
                conn.delete(self.straight, **data)
                data = None
            except (GSAException, error):
                logger.exception('exception during unindexing %r', obj)

    def begin(self):
        pass

    def commit(self, wait=None):
        
        conn = self.getConnection()
        if conn is not None:
            try:
                logger.debug('committing')
                conn.commit()
            except (GSAException, error):
                logger.exception('exception during commit')

    def abort(self):
        conn = self.getConnection()
        if conn is not None:
            logger.debug('aborting')
            conn.abort()
        
    def getConnection(self):
        if self.manager is None:
            self.manager = queryUtility(IGSAConnectionManager)
        if self.manager is not None:
            return self.manager.getIndexConnection()


    def prepareData(self, obj):
        data = {}
        data['url'] = obj.absolute_url()
        data['path'] = obj.absolute_url_path()
        data['last-modified'] = obj.modified().rfc822()
        data['mimetype'] = obj.Format()
        cnt_provider = queryMultiAdapter((obj, obj.REQUEST), IContentProvider)

        data['content'] = None
        if cnt_provider:
            try:
                data['content'], data['content_encoding'] = cnt_provider.content()
            except ConflictError, e:
                raise
            except Exception, e:
                logger.warning('Could not get the object\'s content. Reason: %s' % e)

        if data['content'] is None:
            data['content'] = u"%s - %s" % (safe_unicode(obj.Title()), safe_unicode(obj.Description()))
            data['content_encoding'] = None
        
        # Check the content validity
        badcharresults = BADCHAR_PATTERN.search(data['content'])
        if badcharresults:
            logger.debug('reindexing BAD CHARACTERS url: %s, content: %s' % (data['url'],repr(data['content'][badcharresults.start()-20:badcharresults.start()+20])))        
            return None
            
        # If anonymous has View access, omit the authmethod tag
        pms = obj.permissionsOfRole('Anonymous')
        view_pm = [x for x in pms if x['name'] == 'View']
        if len(view_pm) > 0 and view_pm[0]['selected']:
            data['authmethod'] = "none"
        else:
            data['authmethod'] = "httpbasic"

        mt_data = {}
        catalog = getToolByName(obj, 'portal_catalog')
        schema = catalog.schema()
        wr_obj = self.wrapObject(obj)
        for meta in schema:
            val = getattr(wr_obj, meta, None)
            if callable(val):
                val = val()
            if val:
                mt_data[meta] = val
        
        data['metadata'] = mt_data
        return data
            
    def wrapObject(self, obj):
        """ wrap object with an "IndexableObjectWrapper`, see
            `CatalogTool.catalog_object` for some background """
        portal = getToolByName(obj, 'portal_url', None)
        if portal is None:
            return obj
        portal = portal.getPortalObject()
        wrapper = queryMultiAdapter((obj, portal), IIndexableObjectWrapper)
        if wrapper is None:
            return obj
        wft = getToolByName(obj, 'portal_workflow', None)
        if wft is not None:
            wrapper.update(wft.getCatalogVariablesFor(obj))
        return wrapper