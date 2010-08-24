"""Base class for integration tests, based on ZopeTestCase and CMFTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox CMFSite site with the appropriate
products installed.
"""

from Products.CMFTestCase import CMFTestCase
from Products.salesforcebaseconnector.tests.layer import SalesforceCMFLayer

CMFTestCase.setupCMFSite()

class SalesforceBaseConnectorTestCase(CMFTestCase.CMFTestCase):
    """Base class for integration tests for the 'salesforcebaseconnector' product.
    """

    layer = SalesforceCMFLayer
    
    def afterSetUp(self):
        self.toolbox = self.portal.portal_salesforcebaseconnector
        self._todelete = list() # keep track of ephemeral test data to delete

    def beforeTearDown(self):
        """clean up SF data"""
        if not hasattr(self, '_todelete'):
            return
        ids = self._todelete
        if ids:
            while len(ids) > 200:
                self.toolbox.delete(ids[:200])
                ids = ids[200:]
            self.toolbox.delete(ids)

