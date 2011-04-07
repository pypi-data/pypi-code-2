import doctest
from zope.configuration import xmlconfig
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.layers import (
    FunctionalTesting,
    IntegrationTesting,
)
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile


class CollectiveLayoutAuthpersonalbarLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.layout.authpersonalbar
        xmlconfig.file('configure.zcml', collective.layout.authpersonalbar,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # applyProfile (installProducts is for zope2-style-products)
        applyProfile(portal, 'collective.layout.authpersonalbar:default')

COLLECTIVELAYOUTAUTHPERSONALBAR_FIXTURE = \
                                    CollectiveLayoutAuthpersonalbarLayer()

COLLECTIVELAYOUTAUTHPERSONALBAR_INTEGRATION_TESTING = IntegrationTesting( \
    bases=(COLLECTIVELAYOUTAUTHPERSONALBAR_FIXTURE,),
    name="CollectiveLayoutAuthpersonalbarLayer:Integration")
COLLECTIVELAYOUTAUTHPERSONALBAR_FUNCTIONAL_TESTING = FunctionalTesting( \
    bases=(COLLECTIVELAYOUTAUTHPERSONALBAR_FIXTURE,),
    name="CollectiveLayoutAuthpersonalbarLayer:Functional")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
