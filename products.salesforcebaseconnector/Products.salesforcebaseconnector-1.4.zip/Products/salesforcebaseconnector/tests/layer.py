from Testing.ZopeTestCase import app, close, installProduct
from Products.CMFTestCase.layer import CMFSite
from Products.PloneTestCase.layer import PloneSite
from transaction import commit
from Products.salesforcebaseconnector.tests import sfconfig


class SalesforceCMFLayer(CMFSite):

    @classmethod
    def setUp(cls):
        installProduct('salesforcebaseconnector')
        # add the connector
        root = app()
        portal = root.cmf
        portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        portal.portal_salesforcebaseconnector.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass


class SalesforcePloneLayer(PloneSite):

    @classmethod
    def setUp(cls):
        installProduct('salesforcebaseconnector')
        # add the connector
        root = app()
        portal = root.plone
        portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        portal.portal_salesforcebaseconnector.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass
