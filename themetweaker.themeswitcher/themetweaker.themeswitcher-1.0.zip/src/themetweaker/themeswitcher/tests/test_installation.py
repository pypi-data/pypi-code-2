import unittest
from themetweaker.themeswitcher.tests.test_base import TestCase

class TestInstallation(TestCase):
    """ testing installation """

    def test_install(self):
        quickinstaller = self.portal.portal_quickinstaller
        self.assertTrue(
            quickinstaller.isProductInstalled('themetweaker.themeswitcher'),
            """ThemeSwitcher isn't installed, TestCase failed to install
            'themetweaker.themeswitcher'.""")

    def test_skins_installed(self):
        skins = self.portal.portal_skins
        self.assertTrue(
            'skin_one theme' in skins.selections,
            """Can't find 'skin_one' in the skins tool.""")
        self.assertTrue(
            'skin_two theme' in skins.selections,
            """Can't find 'skin_two' in the skins tool.""")

    def test_default_skin(self):
        skins = self.portal.portal_skins
        self.assertEqual(skins.default_skin, 'Plone Default')

    def test_tab_is_available(self):
        actions = self.portal.portal_actions
        self.assertEqual(actions.object.switcherform.title, 'ThemeSwitcher')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallation))
    return suite