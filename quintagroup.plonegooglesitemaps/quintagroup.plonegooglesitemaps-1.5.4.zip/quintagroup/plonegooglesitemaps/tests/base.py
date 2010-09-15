#
# Tests for quintagroup.plonegooglesitemaps
#

import re, sys
from urllib import urlencode
from StringIO import StringIO
import unittest

from zope.testing import doctestunit
from zope.interface import Interface
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.setup import portal_owner
from Products.PloneTestCase.setup import default_password

from XMLParser import parse, hasURL

import quintagroup.plonegooglesitemaps
from quintagroup.plonegooglesitemaps.config import PROJECTNAME
from quintagroup.plonegooglesitemaps.config import ping_googlesitemap
from quintagroup.plonegooglesitemaps.browser import mobilesitemapview

quintagroup.plonegooglesitemaps.config.testing = 1
quintagroup.plonegooglesitemaps.config.UPDATE_CATALOG = True

PRODUCT = 'quintagroup.plonegooglesitemaps'

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """
    fiveconfigure.debug_mode = True
    import quintagroup.plonegooglesitemaps
    zcml.load_config('configure.zcml', quintagroup.plonegooglesitemaps)
    zcml.load_config('overrides.zcml', quintagroup.plonegooglesitemaps)
    fiveconfigure.debug_mode = False

    ztc.installPackage(PRODUCT)

setup_product()
ptc.setupPloneSite( products=(PRODUCT,))


class IMobileMarker(Interface):
    """Test Marker interface for mobile objects"""


class MixinTestCase(object):
    """ Define layer and common afterSetup method with package installation.
        Package installation on plone site setup impossible because of
        five's registerPackage directive not recognized on module initializing.
    """
    layer = PloneSite

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.workflow = self.portal.portal_workflow
        self.orig_mobile_ifaces = None

    def patchMobile(self):
        # patch mobile sitemap view
        self.orig_mobile_ifaces = mobilesitemapview.MOBILE_INTERFACES
        mobilesitemapview.MOBILE_INTERFACES = [IMobileMarker.__identifier__,]

    def beforeTearDown(self):
        if self.orig_mobile_ifaces is not None:
            mobilesitemapview.MOBILE_INTERFACES = self.orig_mobile_ifaces


class TestCase(MixinTestCase, ptc.PloneTestCase):
    """ For unit tests """


class FunctionalTestCase(MixinTestCase, ptc.FunctionalTestCase):
    """ For functional tests """

    def afterSetUp(self):
        super(FunctionalTestCase, self).afterSetUp()
        self.auth = "%s:%s" % (portal_owner, default_password)

