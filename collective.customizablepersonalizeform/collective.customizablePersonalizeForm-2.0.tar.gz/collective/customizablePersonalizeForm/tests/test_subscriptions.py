#
# Tests subscriptions for additional fields, properties and widgets
#

from Products.CMFPlone.tests import PloneTestCase
from base import CollectiveCPFTestCase

from zope import schema
from zope.component import adapts, getMultiAdapter, getGlobalSiteManager
from zope.interface import implements, Interface 
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.formlib.boolwidgets import CheckBoxWidget

from collective.customizablePersonalizeForm.browser.personalpreferences import ExtendedUserDataPanel
from collective.customizablePersonalizeForm.adapters.adapters import EnhancedUserDataPanelAdapter
from collective.customizablePersonalizeForm.adapters.interfaces import IExtendedUserDataSchema, IExtendedUserDataPanel, IExtendedUserDataWidgets
from collective.customizablePersonalizeForm import CollectiveCustomizablePFMessageFactory as _

from plone.app.users.userdataschema import IUserDataSchemaProvider

default_user = PloneTestCase.default_user

"""
The following adapters can be declared like this:
    <!-- Example -->
    <!--
    EXTRA FIELDS
    <adapter for="*
                  zope.publisher.interfaces.browser.IBrowserRequest"
             provides="collective.customizablePersonalizeForm.adapters.interfaces.IExtendedUserDataSchema"
             factory=".adapters.TestSchemaAdapter"
             name="'test.additional.fields"/>

    EXTRA GETTERS AND SETTERS
    <adapter for="*
                  zope.publisher.interfaces.browser.IBrowserRequest"
             provides="collective.customizablePersonalizeForm.adapters.interfaces.IExtendedUserDataPanel"
             factory=".adapters.TestPropertiesAdapter"
             name="test.additional.properties"/>

    EXTRA WIDGETS
    <adapter for="*
                  zope.publisher.interfaces.browser.IBrowserRequest"
             provides="collective.customizablePersonalizeForm.adapters.interfaces.IExtendedUserDataWidgets"
             factory=".adapters.TestPropertiesAdapter"
             name="test.additional.widgets"/>
    -->
"""

class ITestAdditionalDataSchema(Interface):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """
    test_field = schema.Bool(
        title=_(u'label_test_field_title', default=u'Test field'),
        description=_(u'label_test_field_description', default=u''),
        required=False,
        )

class TestSchemaAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataSchema)
    __name__ = 'test.additional.fields'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getSchema(self):
        return ITestAdditionalDataSchema

class TestPropertiesAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataPanel)
    __name__ = 'test.additional.properties'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getProperties(self):
        return ['test_field']

class TestWidgetAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataWidgets)
    __name__ = 'test.additional.widgets'
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getWidgets(self):
        return [{'field': 'test_field', 'factory' : CheckBoxWidget},
               ]


##############################################
# TESTS

class CollectiveCPFSubscriptionsTestCase(CollectiveCPFTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.personalPrefs = getMultiAdapter((self.portal, self.portal.REQUEST), name='personal-information')
        self.login('manager')
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(TestSchemaAdapter)
        gsm.registerAdapter(TestPropertiesAdapter)
        gsm.registerAdapter(TestWidgetAdapter)

    def testAdditionalSchema(self):
        self.failUnless('test_field' in self.personalPrefs.form_fields.__dict__['__FormFields_byname__'].keys())

    def testAdditionalProperties(self):
        adp = EnhancedUserDataPanelAdapter(self.portal)
        self.failUnless(hasattr(adp, 'test_field')) 

    def testAdditionalWidgets(self):
        self.failUnless( self.personalPrefs.form_fields['test_field'].custom_widget is CheckBoxWidget)
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(CollectiveCPFSubscriptionsTestCase))
    return suite


