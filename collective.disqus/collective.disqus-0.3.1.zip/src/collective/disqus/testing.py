

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig


class DisqusFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.disqus
        xmlconfig.file('configure.zcml', collective.disqus,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.disqus:default')


DISQUS_FIXTURE = DisqusFixture()
DISQUS_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_INTEGRATION_TESTING, DISQUS_FIXTURE,),
        name="Disqus:Integration")
DISQUS_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(PLONE_FUNCTIONAL_TESTING, DISQUS_FIXTURE,),
        name="Disqus:Functional")
