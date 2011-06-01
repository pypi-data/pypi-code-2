from Testing.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import installProduct
from Testing.makerequest import makerequest
from zExceptions import Forbidden

installProduct('PloneHotfix20110531')


class TestHotfix(ZopeTestCase):
    
    def test_AccountPanelSchemaAdapter_patch(self):
        # (note: this test is expected to fail in Plone < 4
        #  where plone.app.users is not present)
        from plone.app.users.browser.account import AccountPanelSchemaAdapter
        from OFS.SimpleItem import SimpleItem
        
        class DummyPortalMembership(object):
            def __init__(self, allowed):
                self.allowed = allowed
            def getMemberById(self, id):
                return id
            def getAuthenticatedMember(self):
                return '(authenticated)'
            def checkPermission(self, permission, context):
                return self.allowed
        
        context = makerequest(SimpleItem('foo'))
        context.portal_membership = DummyPortalMembership(False)

        # no userid specified; edit current user
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('(authenticated)', adapter.context)
        
        # userid in request form; edit current user
        context.REQUEST.form['userid'] = 'bob'
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('(authenticated)', adapter.context)

        # userid in request form for Manager; edit specified user
        context.portal_membership = DummyPortalMembership(True)
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('bob', adapter.context)

        # userid in request other; edit specified user (for registration form)
        context.portal_membership = DummyPortalMembership(False)
        context.REQUEST.set('userid', 'bob')
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('bob', adapter.context)

    def test_safe_html_hasScript_patch(self):
        from Products.PortalTransforms.data import datastream
        from Products.PortalTransforms.transforms.safe_html import SafeHTML
        transform = SafeHTML()
        data_out = datastream('out')

        data_in = """<a href="javascript&amp;#0:alert('1');">click me</a>"""
        transform.convert(data_in, data_out)
        self.assertEqual("""<a>click me</a>""", data_out.getData())

        data_in = """<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgidGVzdCIpOzwvc2NyaXB0Pg==">click me</a>"""
        transform.convert(data_in, data_out)
        self.assertEqual("""<a>click me</a>""", data_out.getData())

        data_in = """<a style="width: expression/**/(alert('xss'))">click me</a>"""
        transform.convert(data_in, data_out)
        self.assertEqual("""<a>click me</a>""", data_out.getData())
    
    def test_safe_html_parse_declaration_patch(self):
        from Products.PortalTransforms.data import datastream
        from Products.PortalTransforms.transforms.safe_html import SafeHTML
        transform = SafeHTML()
        data_out = datastream('out')

        data_in = """<![<a href="javascript:alert('0');">click me</a>"""
        transform.convert(data_in, data_out)
        self.assertEqual("", data_out.getData())

    def test_script_publishing_patch(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        tpl = ZopePageTemplate('selectedTabs', '')
        tpl = makerequest(tpl)
        tpl.REQUEST['PUBLISHED'] = tpl
        self.assertRaises(Forbidden, tpl)

        # make sure we didn't break other templates
        from Products.PageTemplates.PageTemplate import PageTemplate
        tpl = PageTemplate()
        self.assertEqual('', tpl())

    def test_updateUser_patch(self):
        # See https://bugs.launchpad.net/zope-pas/+bug/789858
        from Products.PluggableAuthService.plugins.ZODBUserManager import ZODBUserManager
        zum = ZODBUserManager('zum')
   
        zum.addUser( 'user1', 'user1@example.com', 'password' )
        zum.addUser( 'user2', 'user2@example.com', 'other' )
        self.assertRaises(ValueError,
                          zum.updateUser, 'user1', 'user2@example.com')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHotfix))
    return suite
