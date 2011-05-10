# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer, quickInstallProduct, \
    PLONE_FIXTURE
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig


def create_mock_reporter(values):
    class BugzScoutReporter(object):
        def report(self, uri, username, email, project, area, description):
            new_values = dict(uri=uri, username=username, email=email,
                              project=project, area=area,
                              description=description)
            values.update(new_values)
    return BugzScoutReporter()


class BugzScoutLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        #: Load ZCML for the package being tested.
        import Products.BugzScout
        xmlconfig.file('configure.zcml', Products.BugzScout,
                       context=configurationContext)
        #: Unregister out IBugzScoutReporter so that we don't actually make
        #  external FogBugz requests.
        from Products.BugzScout.interfaces import IBugzScoutReporter
        from zope.component.globalregistry import globalSiteManager
        globalSiteManager.unregisterUtility(provided=IBugzScoutReporter)

    def setUpPloneSite(self, portal):
        #: Install the package in the Plone site.
        quickInstallProduct(portal, 'Products.BugzScout')


BUGZSCOUT_FIXTURE = BugzScoutLayer()

BUGZSCOUT_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(BUGZSCOUT_FIXTURE,),
                       name="BugzScout:Integration")
