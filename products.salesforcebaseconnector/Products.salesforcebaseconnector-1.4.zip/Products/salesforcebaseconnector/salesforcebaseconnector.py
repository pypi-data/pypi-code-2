## Python imports
import logging
import urllib
from beatbox import PythonClient as SalesforceClient
from beatbox import SessionTimeoutError, DEFAULT_SERVER_URL

## Zope imports
from zope.interface import implements

## Plone imports
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
try:
    from App.class_init import InitializeClass
except ImportError:
    # Zope 2.9
    from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ManagePortal

## Interfaces
from interfaces.salesforcebaseconnector import ISalesforceBaseConnector, ISalesforceBaseConnectorInfo, \
    SalesforceRead, SalesforceWrite

logger = logging.getLogger('SalesforceBaseConnector')

def recover_from_session_timeout(func):
    """Decorator for SalesforceBaseConnector methods.  Calls a Salesforce.com
       API call using beatbox, and tries again if there is a session
       timeout."""
    def try_twice(self, *args, **kw):
        logger.debug('Calling %s' % func.__name__)
        try:
            return func(self, *args, **kw)
        except SessionTimeoutError:
            self._resetClient()
            return func(self, *args, **kw)
    return try_twice


class SalesforceBaseConnector (UniqueObject, SimpleItem):
    """A tool for storing/managing connections and connection information when interacting
       with Salesforce.com via beatbox.
    """
    implements(ISalesforceBaseConnector,ISalesforceBaseConnectorInfo)
    
    serverUrl = None
    defaultServerUrl = DEFAULT_SERVER_URL
    
    _v_temp_client = None
    
    def __init__(self):
        self._username = ''
        self._password = ''
    
    id = 'portal_salesforcebaseconnector'
    meta_type = 'Salesforce Base Connector'
    title = 'Connect to an external Salesforce instance'

    security = ClassSecurityInfo()

    manage_options=(( { 'label' : 'Configure Authentication'
                        , 'action' : 'manage_config'
                        },
                      ) + SimpleItem.manage_options
                    )
    
    ##   ZMI methods
    security.declareProtected(ManagePortal, 'manage_config')
    manage_config = PageTemplateFile('www/manageAuthConfig', globals() )
    manage_config._owner = None

    def _login(self):
        # deprecated
        logger.debug('logging into salesforce...')
        client = self._client
        res = client.login(self._username, self._password)
        return res
    
    def _getClient(self):
        # BBB
        logger.warn('The _getClient method of the salesforcebaseconnector '
                    'has been deprecated. Please use the client attribute '
                    'instead.')
        return self.client

    @property
    def _client(self):
        # Clients with open connections are stored on the ZODB database
        # connection. This approach is based on alm.solrindex. See its
        # documentation for a full explanation.
        
        jar = self._p_jar
        oid = self._p_oid
        
        if jar is None or oid is None:
            # Not yet registered in the ZODb, so use a volatile attribute
            client = self._v_temp_client
            if client is None:
                self._v_temp_client = client = SalesforceClient(serverUrl = self.serverUrl,
                                                                cacheTypeDescriptions = True)
        else:
            foreign_connections = getattr(jar, 'foreign_connections', None)
            if foreign_connections is None:
                jar.foreign_connections = foreign_connections = {}
            client = foreign_connections.get(oid)
            if client is None:
                foreign_connections[oid] = client = SalesforceClient(serverUrl = self.serverUrl,
                                                                     cacheTypeDescriptions = True)
        return client

    security.declarePrivate('client')
    @property
    def client(self):
        """Returns this thread's current Salesforce.com connection, or opens
           a new one using the stored credentials."""
        client = self._client
        if not client.isConnected():
             logger.debug('No open connection to Salesforce. Trying to log in...')
             response = client.login(self._username, self._password)
             if not response:
                 raise "Salesforce login failed"
        
        return client

    def _resetClient(self):
        logger.debug('resetting client')
        self._v_temp_client = None
        if self._p_jar and self._p_oid:
            foreign_connections = getattr(self._p_jar, 'foreign_connections', None)
            if foreign_connections is not None and self._p_oid in foreign_connections:
                del foreign_connections[self._p_oid]
        self._v_valid = None

    security.declareProtected(ManagePortal, 'manage_configSalesforceCredentials')
    def manage_configSalesforceCredentials(self, username, password, REQUEST=None, serverUrl=None):
        """Called by the ZMI auth management tab """
        portalMessage = ''
        try:
            self.setCredentials(username, password, serverUrl=serverUrl)
            portalMessage = 'Authentication tested successfully. Username and password saved.'
        except Exception, exc:
            portalMessage = 'The supplied credentials could not be authenticated.  Salesforce exception code: %s' % exc.faultString
        if REQUEST is not None:
            query = urllib.urlencode({
                'username': username,
                'serverUrl': serverUrl,
                'portal_status_message': portalMessage,
                })
            REQUEST.RESPONSE.redirect('%s/manage_config?%s' % (self.absolute_url(),query))

    security.declareProtected(ManagePortal, 'setCredentials')
    def setCredentials(self, username, password, serverUrl=None):
        if serverUrl == DEFAULT_SERVER_URL:
            serverUrl = None

        # do test log in first to confirm valid credentials
        # (will raise exception that can be handled by our caller, if invalid)
        testClient = SalesforceClient(serverUrl = serverUrl)
        testClient.login(username, password)
        
        self.serverUrl = serverUrl
        self._username = username
        self._password = password
        # Disconnect from any previously connected Salesforce instance
        self._resetClient()
        return True
    
    security.declarePublic('validateCredentials')
    def validateCredentials(self):
        """Method that can be called by a remote monitor to confirm that the
        configured credentials are still valid.
        """
        valid = getattr(self, '_v_valid', None)
        if valid is None:
            valid = True
            try:
                testClient = SalesforceClient(serverUrl=self.serverUrl)
                testClient.login(self._username, self._password)
            except:
                valid = False
            self._v_valid = valid
        if valid:
            return 'OK'
    
    security.declareProtected(ManagePortal, 'manage_flushTypeDescriptionCache')
    def manage_flushTypeDescriptionCache(self, REQUEST=None):
        """Purge beatbox's cache of field types for marshalling SF responses"""
        self.client.flushTypeDescriptionsCache()
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_config?portal_status_message=%s' %
                (self.absolute_url(), 'sObject type information purged.'))

    security.declareProtected(ManagePortal, 'setBatchSize')
    @recover_from_session_timeout
    def setBatchSize(self, batchsize):
        """Set the batchsize used by query and queryMore"""
        self.client.batchSize = batchsize
    
    security.declareProtected(ManagePortal, 'getUsername')    
    def getUsername(self):
        """Return the current stored Salesforce username"""
        return self._username

    security.declareProtected(ManagePortal, 'getPassword')
    def getPassword(self):
        """Return the current stored Salesforce password"""
        return self._password
        
    ##
    # Convenience methods not included in Salesforce API
    # #
    
    security.declareProtected(SalesforceRead, 'listFieldsRequiredForCreation')
    def listFieldsRequiredForCreation(self, sObjectType):
        """See .interfaces.salesforcebaseconnector
        """
        dataTypeInfo = self.describeSObjects(sObjectType)[0].fields
        fieldList = []

        for fieldName, fieldData in dataTypeInfo.items():
            if self._isRequired(fieldData):
                fieldList.append(fieldName)

        return fieldList

    def _isRequired(self, fieldData):
        return not fieldData.nillable and not fieldData.defaultedOnCreate and fieldData.createable

    ##
    # Salesforce API -- see .interfaces.salesforcebaseconnector
    ##
    
    ## Accessors
    security.declareProtected(SalesforceRead, 'query')
    def query(self, *args, **kw):
        if len(args) > 1:
            # BBB for old method signature
            return self._BBBquery(*args, **kw)

        soql = args[0]
        return self._query(soql)

    @recover_from_session_timeout
    def _query(self, soql):
        return self.client.query(soql)
    
    def _BBBquery(self, fieldList, sObjectType, whereClause=''):
        # BBB for old method signature
        logger.warn('Called query with deprecated 3-parameter style.  Please '
                    'pass a full SOQL query instead.')
        if sObjectType is None:
            raise ValueError, "Invalid argument: sObjectType must not be None"
        if not fieldList:
            raise ValueError, "Invalid argument: must pass list of desired fields"
        fieldString = ','.join(fieldList)
        soql = 'SELECT %s from %s' % (fieldString, sObjectType)
        if whereClause:
            soql += ' WHERE %s' % (whereClause)
        return self._query(soql)

    security.declareProtected(SalesforceRead, 'search')
    @recover_from_session_timeout
    def search(self, sosl):
        return self.client.search(sosl)

    security.declareProtected(SalesforceRead, 'describeGlobal')
    @recover_from_session_timeout
    def describeGlobal(self):
        return self.client.describeGlobal()

    security.declareProtected(SalesforceRead, 'describeSObjects')
    def describeSObjects(self, sObjectTypes):
        logger.debug('calling describeSObjects')
        # fetch info in batches of 100, as that's the maximum allowed by
        # Salesforce.com
        x = 0
        res = []
        while x < len(sObjectTypes):
            res.extend(self._describeSObjects(sObjectTypes[x:x+100]))
            x += 100
        return res

    @recover_from_session_timeout
    def _describeSObjects(self, sObjectTypes):
        return self.client.describeSObjects(sObjectTypes)

    security.declareProtected(SalesforceRead, 'queryMore')
    @recover_from_session_timeout
    def queryMore(self, queryLocator):
        return self.client.queryMore(queryLocator)

    security.declareProtected(SalesforceRead, 'retrieve')
    def retrieve(self, fields, sObjectType, ids):
        fieldString = ''
        if fields:
            fieldString = ','.join(fields)
        return self._retrieve(fieldString, sObjectType, ids)

    @recover_from_session_timeout
    def _retrieve(self, fieldString, sObjectType, ids):
        return self.client.retrieve(fieldString, sObjectType, ids)

    security.declareProtected(SalesforceRead, 'getDeleted')
    @recover_from_session_timeout
    def getDeleted(self, sObjectType, start, end):
        return self.client.getDeleted(sObjectType, start, end)

    security.declareProtected(SalesforceRead, 'getUpdated')
    @recover_from_session_timeout
    def getUpdated(self, sObjectType, start, end):
        return self.client.getUpdated(sObjectType, start, end)

    security.declareProtected(SalesforceRead, 'getUserInfo')
    @recover_from_session_timeout
    def getUserInfo(self):
        return self.client.getUserInfo()

    security.declareProtected(SalesforceRead, 'describeTabs')
    @recover_from_session_timeout
    def describeTabs(self):
        return self.client.describeTabs()


    ## Mutators
    security.declareProtected(SalesforceWrite, 'create')
    @recover_from_session_timeout
    def create(self, sObjects):
        return self.client.create(sObjects)

    security.declareProtected(SalesforceWrite, 'update')
    @recover_from_session_timeout
    def update(self, sObjects):
        return self.client.update(sObjects)

    security.declareProtected(SalesforceWrite, 'upsert')
    @recover_from_session_timeout
    def upsert(self, externalIdName, sObjects):
        return self.client.upsert(externalIdName, sObjects)

    security.declareProtected(SalesforceWrite, 'delete')
    @recover_from_session_timeout
    def delete(self, ids):
        return self.client.delete(ids)
    
InitializeClass(SalesforceBaseConnector)