import logging

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Cache import Cacheable
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

# PAS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

logger = logging.getLogger("salesforceauthplugin")

class SalesforceBasePluginMixin(BasePlugin, Cacheable):
    """Our base plugin for mixin with interface specific
       plugins
    """
    security = ClassSecurityInfo()
    meta_type = 'Salesforce Auth Plugin'
    
    #
    # Internal API
    #
    security.declarePrivate("_initSalesforceConnection")
    def _initSalesforceConnection(self):
        logger.debug('Need to initialize Salesforce Base Connector')
        pas=self._getPAS()
        site=aq_parent(pas)
        self.baseconnector = getToolByName(site, 'portal_salesforcebaseconnector')
    
    security.declarePrivate("_getSFConnection")
    def _getSFConnection(self):
        if not hasattr(self, "baseconnector") or self.baseconnector is None:
            self._initSalesforceConnection()
        return self.baseconnector

InitializeClass(SalesforceBasePluginMixin)
