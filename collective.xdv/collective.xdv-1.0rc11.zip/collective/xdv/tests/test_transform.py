import Globals
import os.path

from lxml import etree

from unittest import defaultTestLoader
from urllib2 import HTTPError

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.Five.testbrowser import Browser
from Products.CMFCore.Expression import Expression, getExprContext

from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from collective.xdv.interfaces import ITransformSettings
from collective.xdv.transform import getCache
from collective.xdv.header import setHeader
from collective.xdv.utils import InternalResolver, PythonResolver, resolvePythonURL

from xdv.compiler import compile_theme

from Products.CMFCore.utils import getToolByName

@onsetup
def setup_product():
    import collective.xdv
    zcml.load_config('configure.zcml', collective.xdv)

setup_product()
ptc.setupPloneSite(products=['collective.xdv'])

class TestCase(ptc.FunctionalTestCase):
    
    def afterSetUp(self):
        # Enable debug mode always to ensure cache is disabled by default
        Globals.DevelopmentMode = True
        
        self.settings = getUtility(IRegistry).forInterface(ITransformSettings)
        
        self.settings.enabled = False
        self.settings.domains = set([u'nohost:80', u'nohost'])
        self.settings.theme = resolvePythonURL(u'python://collective.xdv/tests/theme.html')
        self.settings.rules = resolvePythonURL(u'python://collective.xdv/tests/rules.xml')
        self.settings.notheme = set([u'^.*/emptypage$', 
                                     u'^.*/manage$', 
                                     u'^.*/manage_(?!translations_form)[^/]+$', 
                                     u'^.*/image_view_fullscreen$',
                                     u'^.*/referencebrowser_popup(\?.*)?$',
                                     u'^.*/error_log(/.*)?$',
                                     u'^.*/aq_parent(/.*)?$'])
        theme_other = resolvePythonURL(u'python://collective.xdv/tests/othertheme.html')
        self.settings.alternate_themes = [u"^.*/news.*$ %s %s" % (theme_other, self.settings.rules),]
        
    def evaluate(self, context, expression):
        ec = getExprContext(context, context)
        expr = Expression(expression)
        return expr(ec)
    
    def test_no_effect_if_not_enabled(self):
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failUnless("Accessibility" in browser.contents)
        
        # The theme
        self.failIf("This is the theme" in browser.contents)
    
    def test_theme_enabled(self):
        self.settings.enabled = True
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
    
    def test_internal_resolver(self):
        compiler_parser = etree.XMLParser()
        compiler_parser.resolvers.add(InternalResolver())
        compile_theme(self.settings.rules, self.settings.theme, compiler_parser=compiler_parser)
    
    def test_python_resolver(self):
        compiler_parser = etree.XMLParser()
        compiler_parser.resolvers.add(PythonResolver())
        compile_theme(self.settings.rules, self.settings.theme, compiler_parser=compiler_parser)
    
    def test_python_uris(self):
        self.settings.enabled = True
        
        # We can use a sub-package or a directory since tests is a python
        # package
        self.settings.theme = u'python://collective.xdv.tests/theme.html'
        self.settings.rules = u'python://collective.xdv/tests/rules.xml'
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
    
    def test_theme_stored_in_plone_site(self):
        # We'll upload the theme files to the Plone site root
        rules_contents = open(os.path.join(os.path.split(__file__)[0], 'rules.xml'))
        theme_contents = open(os.path.join(os.path.split(__file__)[0], 'theme.html'))
        self.portal.manage_addDTMLMethod('theme.html', file=theme_contents)
        self.portal.manage_addDTMLMethod('rules.xml', file=rules_contents)

        # These paths should be relative to the Plone site root
        self.settings.theme = u'/theme.html'
        self.settings.rules = u'/rules.xml'
        self.settings.enabled = True

        browser = Browser()
        browser.open(self.portal.absolute_url())

        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)

    def test_theme_stored_in_plone_site_works_with_virtual_host(self):
        # We'll upload the theme files to the Plone site root
        rules_contents = open(os.path.join(os.path.dirname(__file__), 'rules.xml'))
        theme_contents = open(os.path.join(os.path.dirname(__file__), 'theme.html'))
        self.portal.manage_addDTMLMethod('theme.html', file=theme_contents)
        self.portal.manage_addDTMLMethod('rules.xml', file=rules_contents)

        # These paths should be relative to the Plone site root
        self.settings.theme = u'/theme.html'
        self.settings.rules = u'/rules.xml'
        self.settings.domains = set([u'example.org/fizz/buzz/fizzbuzz'])
        self.settings.enabled = True
        
        from Products.SiteAccess import VirtualHostMonster
        VirtualHostMonster.manage_addVirtualHostMonster(self.app, 'virtual_hosting')
        
        import transaction
        transaction.commit()
        
        portalURL = self.portal.absolute_url()
        prefix = '/'.join(portalURL.split('/')[:-1])
        suffix = portalURL.split('/')[-1]
        
        vhostURL = "%s/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/" % (prefix,suffix)
        
        browser = Browser()
        browser.open(vhostURL)
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents) 

    def test_absolute_prefix_disabled(self):
        self.settings.enabled = True
        self.settings.absolute_prefix = None
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        self.failUnless('<img src="relative.jpg" />' in browser.contents)
    
    def test_absolute_prefix_enabled_uri(self):
        self.settings.enabled = True
        self.settings.absolute_prefix = u'http://example.com'
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        self.failIf('<img src="relative.jpg" />' in browser.contents)
        self.failUnless('<img src="http://example.com/relative.jpg" />' in browser.contents)
    
    def test_absolute_prefix_enabled_path(self):
        self.settings.enabled = True
        self.settings.absolute_prefix = u'/foo'
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        self.failIf('<img src="relative.jpg" />' in browser.contents)
        self.failUnless('<img src="/plone/foo/relative.jpg" />' in browser.contents)
    
    def test_absolute_prefix_enabled_path_vhosting(self):
        from Products.SiteAccess import VirtualHostMonster
        VirtualHostMonster.manage_addVirtualHostMonster(self.app, 'virtual_hosting')
        
        import transaction
        transaction.commit()
        
        self.settings.enabled = True
        self.settings.absolute_prefix = u'/foo'
        self.settings.domains = set([u'example.org/fizz/buzz/fizzbuzz'])
        
        portalURL = self.portal.absolute_url()
        prefix = '/'.join(portalURL.split('/')[:-1])
        suffix = portalURL.split('/')[-1]
        
        vhostURL = "%s/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/" % (prefix,suffix)
        
        browser = Browser()
        browser.open(vhostURL)
        
        self.failIf('<img src="relative.jpg" />' in browser.contents)
        self.failUnless('<img src="/fizz/buzz/fizzbuzz/foo/relative.jpg" />' in browser.contents)    
    
    def test_theme_installed_invalid_config(self):
        self.settings.enabled = True
        self.settings.theme = u"invalid"
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failUnless("Accessibility" in browser.contents)
        
        # The theme
        self.failIf("This is the theme" in browser.contents)
        
    def test_notheme_path(self):
        
        self.setRoles(['Manager'])
        if not 'front-page' in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'front-page')
        
        self.settings.enabled = True
        self.settings.notheme = set([u'^.*/front-page$'])
        
        browser = Browser()
        browser.open(self.portal.absolute_url() + '/front-page')
        self.failIf("This is the theme" in browser.contents)

    def test_non_html_content(self):
        
        self.settings.enabled = True
        self.settings.theme = u"invalid"
        
        browser = Browser()
        browser.open(self.portal.absolute_url() + '/document_icon.gif')
        # The theme
        self.failIf("This is the theme" in browser.contents)

    def test_outside_domain(self):
        
        self.settings.enabled = True
        self.settings.domains = set([u"www.example.org", u"www.example.org:80"])
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failUnless("Accessibility" in browser.contents)
        
        # The theme
        self.failIf("This is the theme" in browser.contents)
        
    def test_non_debug_mode_cache(self):
        
        Globals.DevelopmentMode = False
        self.settings.enabled = True
        
        # Sneakily seed the cache with dodgy data
        
        theme = unicode(os.path.join(os.path.split(__file__)[0], 'othertheme.html'))
        rules = unicode(os.path.join(os.path.split(__file__)[0], 'rules.xml'))
        theme_id = u"default"
        compiled_theme = compile_theme(rules, theme)
        transform = etree.XSLT(compiled_theme)
        
        getCache(self.settings, self.portal.absolute_url()).update_transform(theme_id, transform)
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the other theme" in browser.contents)
        
        # Now invalide the cache by touching the settings utility
        
        self.settings.enabled = False
        self.settings.enabled = True
        
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)

    def test_resource_condition(self):
        
        portal_css = getToolByName(self.portal, 'portal_css')
        portal_css.setDebugMode(True)
        
        # shown in both
        thirdLastResource = portal_css.resources[-3]
        thirdLastResource.setExpression('')
        thirdLastResource.setRendering('link')
        thirdLastResource.setEnabled(True)
        
        # only show in theme
        secondToLastResource = portal_css.resources[-2]
        secondToLastResource.setExpression('request/HTTP_X_XDV | nothing')
        secondToLastResource.setRendering('link')
        secondToLastResource.setEnabled(True)
        
        # only show when theme is disabled
        lastResource = portal_css.resources[-1]
        lastResource.setExpression('not:request/HTTP_X_XDV | nothing')
        lastResource.setRendering('link')
        lastResource.setEnabled(True)
        
        portal_css.cookResources()
        
        # First try without the theme
        self.settings.enabled = False
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        self.failUnless(thirdLastResource.getId() in browser.contents)
        self.failIf(secondToLastResource.getId() in browser.contents)
        self.failUnless(lastResource.getId() in browser.contents)
        
        self.failUnless("Welcome to Plone" in browser.contents)
        self.failUnless("Accessibility" in browser.contents)
        self.failIf("This is the theme" in browser.contents)
        
        # Now enable the theme and try again
        self.settings.enabled = True
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        self.failUnless(thirdLastResource.getId() in browser.contents)
        self.failUnless(secondToLastResource.getId() in browser.contents)
        self.failIf(lastResource.getId() in browser.contents)
        
        self.failUnless("Welcome to Plone" in browser.contents)
        self.failIf("Accessibility" in browser.contents)
        self.failUnless("This is the theme" in browser.contents)
    
    def test_enabled_check(self):
        
        # Simulate pre-traversal
        request = self.app.REQUEST
        class DummyEvent(object):
            def __init__(self, request):
                self.request = request
        
        self.settings.enabled = False
        self.settings.domains = set([u'nohost', u'nohost:80'])
        
        setHeader(None, DummyEvent(request))
        value = self.portal.restrictedTraverse('@@xdv-check/enabled')()
        self.failIf(value)
        
        self.settings.enabled = True
        
        setHeader(None, DummyEvent(request))
        value = self.portal.restrictedTraverse('@@xdv-check/enabled')()
        self.failUnless(value)
        del request.environ['HTTP_X_XDV'] # clear for test below
        
        self.settings.domains = set([u'www.example.com', u'www.example.com:80'])
        
        setHeader(None, DummyEvent(request))
        value = self.portal.restrictedTraverse('@@xdv-check/enabled')()
        self.failIf(value)
        
        
    def test_enabled_domain_check(self):
        self.settings.enabled = False
        self.settings.domains = set([u'nohost', u'nohost:80'])
        
        value = self.portal.restrictedTraverse('@@xdv-check/domain_enabled')()
        self.failUnless(value)
        
        self.settings.enabled = True
        value = self.portal.restrictedTraverse('@@xdv-check/domain_enabled')()
        self.failUnless(value)
        
        self.settings.domains = set([u'www.example.com', u'www.example.com:80'])
        value = self.portal.restrictedTraverse('@@xdv-check/domain_enabled')()
        self.failIf(value)
    
    def test_theme_different_path(self):
        self.settings.enabled = True
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
        
        browser.open(self.portal.news.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("News" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the other theme" in browser.contents)
    
    def test_theme_for_404(self):
        self.settings.enabled = True
        browser = Browser()
        error = None
        try:
            browser.open('%s/404_page' % self.portal.absolute_url())
        except HTTPError, e:
            error = e
        self.assertEquals(error.code, 404)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)

    def test_resource_condition_404(self):
        
        portal_css = getToolByName(self.portal, 'portal_css')
        portal_css.setDebugMode(True)
        
        # shown in both
        thirdLastResource = portal_css.resources[-3]
        thirdLastResource.setExpression('')
        thirdLastResource.setRendering('link')
        thirdLastResource.setEnabled(True)
        
        # only show in theme
        secondToLastResource = portal_css.resources[-2]
        secondToLastResource.setExpression('request/HTTP_X_XDV | nothing')
        secondToLastResource.setRendering('link')
        secondToLastResource.setEnabled(True)
        
        # only show when theme is disabled
        lastResource = portal_css.resources[-1]
        lastResource.setExpression('not:request/HTTP_X_XDV | nothing')
        lastResource.setRendering('link')
        lastResource.setEnabled(True)
        
        portal_css.cookResources()
        
        self.settings.enabled = True
        browser = Browser()
        
        try:
            browser.open('%s/404_page' % self.portal.absolute_url())
        except HTTPError, e:
            error = e
        self.assertEquals(error.code, 404)
        
        self.failUnless(thirdLastResource.getId() in browser.contents)
        self.failUnless(secondToLastResource.getId() in browser.contents)
        self.failIf(lastResource.getId() in browser.contents)
        
        self.failUnless("This is the theme" in browser.contents)
    
    def test_includes(self):
        self.setRoles(('Manager',))
        
        one = open(os.path.join(os.path.split(__file__)[0], 'one.html'))
        two = open(os.path.join(os.path.split(__file__)[0], 'two.html'))
        
        # Create some test content in the portal root
        self.portal.manage_addDTMLMethod('alpha', file=one)
        self.portal.manage_addDTMLMethod('beta', file=two)
        
        one.seek(0)
        two.seek(0)
        
        # Create some different content in a subfolder
        self.portal.invokeFactory('Folder', 'subfolder')
        self.portal['portal_workflow'].doActionFor(self.portal['subfolder'], 'publish')
        
        self.portal['subfolder'].manage_addDTMLMethod('alpha', file=two)
        self.portal['subfolder'].manage_addDTMLMethod('beta', file=one)
        
        # Set up XDV
        self.settings.theme = u'python://collective.xdv.tests/includes.html'
        self.settings.rules = u'python://collective.xdv/tests/includes.xml'
        self.settings.enabled = True
        
        browser = Browser()
        
        # At the root if the site, we should pick up 'one' for alpha (absolute
        # path, relative to site root) and 'two' for beta (relative path,
        # relative to current directory)
        
        browser.open(self.portal.absolute_url())
        self.failUnless('<div id="alpha">Number one</div>' in browser.contents)
        self.failUnless('<div id="beta">Number two</div>' in browser.contents)
        
        # In the subfolder, we've reversed alpha and beta. We should now get
        # 'one' twice, since we still get alpha from the site root.
        
        browser.open(self.portal['subfolder'].absolute_url())
        self.failUnless('<div id="alpha">Number one</div>' in browser.contents)
        self.failUnless('<div id="beta">Number one</div>' in browser.contents)
        
def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
