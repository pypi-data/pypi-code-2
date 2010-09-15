from base import *

class TestInstallation(ptc.FunctionalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.qi = getToolByName(self.portal, 'portal_quickinstaller', None)
        self.cp = getToolByName(self.portal, 'portal_controlpanel', None)
        self.st = getToolByName(self.portal, 'portal_skins', None)
        self.qi.installProduct(PRODUCT_NAME)

    def getLayers(self):
        return LAYERS + [LAYER_STATIC_CAPTCHAS]

    def testPropertysheetInstall(self):
        pp = getToolByName(self.portal, 'portal_properties')
        self.assert_(PROPERTY_SHEET in pp.objectIds(), 'Property sheet isn\'t found')

    def testPropertysheetUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        pp = getToolByName(self.portal, 'portal_properties')
        self.assert_(not PROPERTY_SHEET in pp.objectIds(),
            'Property sheet found after uninstallation')

    def testConfigletInstall(self):
        self.assert_(CONFIGLET_ID in [a.getId() for a in self.cp.listActions()], 'Configlet not found')

    def testConfigletUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True,'%s is already installed' % PRODUCT_NAME)
        self.assert_(not CONFIGLET_ID in [a.getId() for a in self.cp.listActions()], 'Configlet found after uninstallation')

    def testSkinsInstall(self):
        skinstool = self.st
        layers = self.getLayers()
        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map(str.strip, path.split(','))
            for layer in layers:
                self.assert_(layer.split('/')[0] in skinstool.objectIds(), '%s directory view not found in portal_skins after installation' % layer)
                self.assert_(layer in path, '%s layer not found in %s' % (PRODUCT_NAME, skin))

    def testSkinsUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True,'%s is already installed' % PRODUCT_NAME)
        skinstool = self.st
        layers = self.getLayers()
        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map(str.strip, path.split(','))
            for layer in layers:
                self.assert_(not layer.split('/')[0] in skinstool.objectIds(), '%s directory view found in portal_skins after uninstallation' % layer)
                self.assert_(not layer in path, '%s layer found in %s after uninstallation' % (layer, skin))

    def testToolInstall(self):
        self.assert_(TOOL_ID in self.portal.objectIds())

    def testToolUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True, 
            '%s is already installed' % PRODUCT_NAME)
        self.assert_(not TOOL_ID in self.portal.objectIds())

    def testCaptchaKey(self):
        ck = getattr(self.portal, CAPTCHA_KEY)
        self.assert_(ck)
        self.assertEqual(len(ck), 8)
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assert_(not self.portal.hasProperty(CAPTCHA_KEY))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallation))
    return suite
