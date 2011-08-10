from Testing import ZopeTestCase as ztc
from zope.testing.doctestunit import DocFileSuite
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.GenericSetup import EXTENSION, profile_registry
from collective.testcaselayer import ptc as tcl_ptc
import unittest
from Products.Archetypes.examples import *


DEPS = ('MimetypesRegistry', 'PortalTransforms', 'Archetypes', 'ATContentTypes', 'kupu')
for product in DEPS:
    ztc.installProduct(product, 1)


class InstallLayer(tcl_ptc.BasePTCLayer):

    def afterSetUp(self):
        import collective.updatelinksoncopy
        zcml.load_config('configure.zcml',
                         collective.updatelinksoncopy)

        profile_registry.registerProfile('Archetypes_sampletypes',
            'Archetypes Sample Content Types',
            'Extension profile including Archetypes sample content types',
            'profiles/sample_types',
            'Products.Archetypes',
            EXTENSION)

        self.addProfile('Products.Archetypes:Archetypes_sampletypes')


class TestCase(ptc.FunctionalTestCase):

    def afterSetUp(self):
        portal = self.portal
        self.setRoles(['Manager',])
        self.kupu = portal.kupu_library_tool
        self.kupu.configure_kupu(captioning=True, linkbyuid=True)


ptc.setupPloneSite(products=['ATContentTypes', 'kupu'])
install_layer = InstallLayer([ptc.FunctionalTestCase.layer])

def test_suite():
    suite = (
        ztc.ZopeDocFileSuite(
            'textlinks.txt', package='collective.updatelinksoncopy',
            test_class=TestCase),
        ztc.ZopeDocFileSuite(
            'referencefields.txt', package='collective.updatelinksoncopy',
            test_class=TestCase),
        DocFileSuite(
            'handlers.py', package='collective.updatelinksoncopy',
            ),
        ztc.ZopeDocFileSuite(
            'edgecases.txt', package='collective.updatelinksoncopy',
            test_class=TestCase),
        )

    suite[0].layer = install_layer
    suite[1].layer = install_layer
    return unittest.TestSuite(suite)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
