from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig


class ViewPortletManagerFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.viewportletmanager
        xmlconfig.file('configure.zcml', collective.viewportletmanager,
                       context=configurationContext)
        xmlconfig.file('overrides.zcml', collective.viewportletmanager,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.viewportletmanager:default')


MYPACKAGE_FIXTURE = ViewPortletManagerFixture()
MYPACKAGE_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_INTEGRATION_TESTING, MYPACKAGE_FIXTURE,),
        name="ViewPortletManager:Integration")
