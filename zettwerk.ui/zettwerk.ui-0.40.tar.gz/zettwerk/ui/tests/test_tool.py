import unittest
import os
import urllib2
from StringIO import StringIO
import zipfile
from plone.testing.z2 import Browser
from mocker import Mocker

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from base import ZETTWERK_UI_INTEGRATION_TESTING
from base import ZETTWERK_UI_THEMES_INTEGRATION_TESTING


class TestTool(unittest.TestCase):

    layer = ZETTWERK_UI_INTEGRATION_TESTING

    def test_cp_view(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tool = getToolByName(portal, 'portal_ui_tool')
        view = getMultiAdapter((tool, request),
                               name='ui-controlpanel')
        content = view()
        self.assertTrue(content.find('class="template-ui-controlpanel') != -1)

        ## search the 3 fieldsets
        fieldset = '<fieldset id="fieldset-settings">'
        self.assertTrue(content.find(fieldset) != -1)
        fieldset = '<fieldset id="fieldset-theme">'
        self.assertTrue(content.find(fieldset) != -1)
        fieldset = '<fieldset id="fieldset-themeroller">'
        self.assertTrue(content.find(fieldset) != -1)

    def test_cp_js_translations(self):
        ## thats a bit odd, and mainly for coverage
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')
        self.assertTrue(tool.cp_js_translations().startswith('var '))

    def test_js(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')

        self.assertTrue(tool.enableFonts)
        self.assertTrue(tool.js().find('enableFonts()') != -1)
        tool.enableFonts = False
        self.assertTrue(tool.js().find('enableFonts()') == -1)

        self.assertTrue(tool.enableDialogs)
        self.assertTrue(tool.js().find('enableDialogs()') != -1)
        tool.enableDialogs = False
        self.assertTrue(tool.js().find('enableDialogs()') == -1)

        self.assertTrue(tool.enableStatusMessage)
        self.assertTrue(tool.js().find('enableStatusMessage()') != -1)
        tool.enableStatusMessage = False
        self.assertTrue(tool.js().find('enableStatusMessage()') == -1)

        self.assertTrue(tool.enableForms)
        self.assertTrue(tool.js().find('enableForms()') != -1)
        tool.enableForms = False
        self.assertTrue(tool.js().find('enableForms()') == -1)

        self.assertTrue(tool.enableTabs)
        self.assertTrue(tool.js().find('enableTabs()') != -1)
        tool.enableTabs = False
        self.assertTrue(tool.js().find('enableTabs()') == -1)

        self.assertTrue(tool.enableGlobalTabs)
        self.assertTrue(tool.js().find('enableGlobalTabs()') != -1)
        tool.enableGlobalTabs = False
        self.assertTrue(tool.js().find('enableGlobalTabs()') == -1)

        self.assertTrue(tool.enablePortlets)
        self.assertTrue(tool.js().find('enablePortlets()') != -1)
        tool.enablePortlets = False
        self.assertTrue(tool.js().find('enablePortlets()') == -1)

        self.assertTrue(tool.enableFooter)
        self.assertTrue(tool.js().find('enableFooter()') != -1)
        tool.enableFooter = False
        self.assertTrue(tool.js().find('enableFooter()') == -1)

        self.assertTrue(tool.enableEditBar)
        self.assertTrue(tool.js().find('enableEditBar()') != -1)
        tool.enableEditBar = False
        self.assertTrue(tool.js().find('enableEditBar()') == -1)

        self.assertTrue(tool.js().find('removeRules()') != -1)

        ## and the translations are also included
        self.assertTrue(tool.js().find('var sorry_only_firefox') != -1)

    def test_css(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')

        self.assertEquals(tool.theme, '')
        self.assertTrue(tool.css().find('zettwerk.ui.themes') == -1)
        tool.theme = 'tester'
        self.assertTrue(tool.css().find('/tester/') != -1)

        self.assertTrue(tool.enableForms)
        self.assertTrue(tool.css().find('#searchGadget') != -1)
        tool.enableForms = False
        self.assertTrue(tool.css().find('#searchGadget') == -1)

        self.assertTrue(tool.enableStatusMessage)
        self.assertTrue(tool.css().find('.ui-custom-status-container') != -1)
        tool.enableStatusMessage = False
        self.assertTrue(tool.css().find('.ui-custom-status-container') == -1)

        self.assertTrue(tool.enableTabs)
        self.assertTrue(tool.css().find('.ui-tabs-nav') != -1)
        tool.enableTabs = False
        self.assertTrue(tool.css().find('.ui-tabs-nav') != -1)
        tool.enableGlobalTabs = False
        self.assertTrue(tool.css().find('.ui-tabs-nav') == -1)

        self.assertTrue(tool.enableFooter)
        self.assertTrue(tool.css().find('#portal-footer') != -1)
        tool.enableFooter = False
        self.assertTrue(tool.css().find('#portal-footer') == -1)

        self.assertTrue(tool.enablePersonalTool)
        self.assertTrue(tool.css().find('.actionMenu') != -1)
        tool.enablePersonalTool = False
        self.assertTrue(tool.css().find('.actionMenu') == -1)

    def test__redirectToCPView(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')

        result = tool._redirectToCPView()
        self.assertTrue(result.endswith('@@ui-controlpanel'))

        result = tool._redirectToCPView(u'tester')
        from Products.statusmessages.interfaces import IStatusMessage
        status_messages = IStatusMessage(self.layer['request']) \
            .showStatusMessages()
        self.assertEquals(len(status_messages), 1)
        self.assertEquals(status_messages[0].message, u'tester')
        ## cleanup the status messages by calling the browser
        abs_url = portal.absolute_url()
        browser = Browser(portal)
        browser.open(abs_url)

    def test__prepareUIDownloadUrl(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')
        result = tool._prepareUIDownloadUrl('hash')
        from zettwerk.ui.tool.tool import UI_DOWNLOAD_URL

        self.assertTrue(result.startswith(UI_DOWNLOAD_URL))
        self.assertTrue(result.endswith('ui-version=1.8'))


class TestTooltWithThemess(unittest.TestCase):

    layer = ZETTWERK_UI_THEMES_INTEGRATION_TESTING

    def test__rebuildThemeHashes_empty(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')

        self.assertTrue(tool.themeHashes is None)
        tool._rebuildThemeHashes()
        from persistent.mapping import PersistentMapping
        self.assertTrue(isinstance(tool.themeHashes, PersistentMapping))

    def test__rebuildThemeHashes_with_theme(self):
        ## prepare a test file
        from zettwerk.ui.filesystem import CSS_FILENAME
        from zettwerk.ui.filesystem import DOWNLOAD_HOME
        theme_dir = 'tester'
        os.mkdir(os.path.join(DOWNLOAD_HOME, theme_dir))
        f = file(os.path.join(DOWNLOAD_HOME, theme_dir, CSS_FILENAME), 'w')
        f.write("foo\n" * 10)
        f.write("bar\n" * 20)
        f.write(" * To view and modify this theme, visit ")
        f.write("http://jqueryui.com/themeroller/?hash=xxx\n")
        f.write("foo\n" * 20)
        f.close()

        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')
        tool._rebuildThemeHashes()
        self.assertEquals(tool.themeHashes[theme_dir],
                          'hash=xxx\n')

    def test_createDLDirectory(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')
        tool.createDLDirectory()

        from Products.statusmessages.interfaces import IStatusMessage
        status_messages = IStatusMessage(self.layer['request']) \
            .showStatusMessages()
        self.assertEquals(len(status_messages), 1)
        self.assertEquals(status_messages[0].message, u'Directory created')

    def test_handleDownload(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')

        ## pre check, that there is no theme enabled
        self.assertEquals(tool.theme, '')

        ## we need a mocker to fake the download
        self.mocker = Mocker()
        self.fake_urllib2 = self.mocker.replace(urllib2)

        ## an url to download
        test_hash = 'hash'
        url = tool._prepareUIDownloadUrl(test_hash)

        ## and a temporary zipfile to test
        s = StringIO()
        z = zipfile.ZipFile(s, 'w')
        content = 'irrelevant'
        z.writestr('css/custom-theme/something.css',
                   content)
        z.writestr('css/ignored.css',
                   content)
        z.close()
        s.seek(0)

        ## setup the fake
        self.fake_urllib2.urlopen(url)
        self.mocker.result(s)

        ## and test it
        with self.mocker:
            tool.handleDownload('tester', test_hash)
            ## this results in an enabled theme called 'tester'
            self.assertEquals(tool.theme, 'tester')

    def test_handleDownload_corrupt(self):
        portal = self.layer['portal']
        tool = getToolByName(portal, 'portal_ui_tool')

        ## pre check, that there is no theme enabled
        self.assertEquals(tool.theme, '')

        ## we need a mocker to fake the download
        self.mocker = Mocker()
        self.fake_urllib2 = self.mocker.replace(urllib2)

        ## an url to download
        test_hash = 'hash'
        url = tool._prepareUIDownloadUrl(test_hash)

        ## and a temporary "corrupt" zipfile to test
        s = StringIO()

        ## setup the fake
        self.fake_urllib2.urlopen(url)
        self.mocker.result(s)

        ## and test it
        with self.mocker:
            tool.handleDownload('tester', test_hash)
            ## extraction should be failed, so the theme should not be changed
            self.assertEquals(tool.theme, '')

            ## and the error status message should be set
            from Products.statusmessages.interfaces import IStatusMessage
            messages = IStatusMessage(self.layer['request']).show()
            self.assertEquals(len(messages), 1)
            self.assertEquals(messages[0].type, u'error')
