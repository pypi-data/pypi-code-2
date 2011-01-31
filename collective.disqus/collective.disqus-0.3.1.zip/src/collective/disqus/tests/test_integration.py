
import unittest2 as unittest

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.testing import applyProfile

from collective.disqus.testing import DISQUS_INTEGRATION_TESTING


class Test(unittest.TestCase):

    layer = DISQUS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def uninstall(self):
        applyProfile(self.portal, 'collective.disqus:uninstall')

    def test_displayviews(self):
        portal_types = self.layer['portal'].portal_types

        self.assertIn('disqus_summary_listing',
                      portal_types.get('Folder').view_methods)
        self.assertIn('disqus_summary_listing',
                      portal_types.get('Topic').view_methods)

        self.uninstall()

        self.assertNotIn('disqus_summary_listing',
                         portal_types.get('Folder').view_methods)
        self.assertNotIn('disqus_summary_listing',
                         portal_types.get('Topic').view_methods)

    def test_viewlets(self):
        storage = getUtility(IViewletSettingsStorage)
        skins = [skin.token for skin in getUtility(IVocabularyFactory,
                    'plone.app.vocabularies.Skins')(self.portal)]

        # plone.comments viewlet should be hidden
        for skin in skins:
            if skin in storage._hidden.keys() and \
               'plone.belowcontent' in storage._hidden[skin]:
                self.assertIn('plone.comments',
                              storage._hidden[skin]['plone.belowcontent'])

        self.uninstall()

        # plone.comments viewlet should be unhidden
        # and collective.disqus hidden
        for skin in skins:
            if skin in storage._hidden.keys() and \
               'plone.belowcontent' in storage._hidden[skin]:
                self.assertNotIn('plone.comments',
                              storage._hidden[skin]['plone.belowcontent'])
                self.assertIn('collective.disqus',
                              storage._hidden[skin]['plone.belowcontent'])

    def test_controlpanel(self):
        controlpanel = self.portal.portal_controlpanel
        self.assertEqual(controlpanel.getActionObject(
                         'Products/DisqusConfig').visible, 1)
        self.uninstall()
        self.assertEqual(controlpanel.getActionObject(
                         'Products/DisqusConfig').visible, 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite
