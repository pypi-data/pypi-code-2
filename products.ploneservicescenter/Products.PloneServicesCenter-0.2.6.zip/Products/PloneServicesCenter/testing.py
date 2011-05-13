from plone.testing import z2
from plone.app import testing

from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName


class ServicesFixture(testing.PloneSandboxLayer):
    default_bases = (testing.PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import Products.PloneServicesCenter
        self.loadZCML(package=Products.PloneServicesCenter)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.ArchAddOn')
        z2.installProduct(app, 'Products.PloneServicesCenter')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        getToolByName(portal, 'portal_quickinstaller').installProduct(
            'Products.ArchAddOn')
        self.applyProfile(portal, 'Products.PloneServicesCenter:default')

        # Publish the folders
        z2.login(aq_parent(portal).acl_users, 'admin')
        wftool = getToolByName(portal, 'portal_workflow')
        for id_ in ('case-studies', 'sites', 'providers'):
            wftool.doActionFor(portal.support[id_], 'publish')
        z2.logout()

SERVICES_FIXTURE = ServicesFixture()
SERVICES_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(SERVICES_FIXTURE,), name="Services:Functional")
