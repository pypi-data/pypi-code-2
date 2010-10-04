import unittest

from zope.interface import alsoProvides
from zope.interface.verify import verifyObject, verifyClass

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase

# interfaces
from archetypes.schemaextender.interfaces import ISchemaExtender
from collective.salesforce.rsvp import interfaces

# classes
from collective.salesforce.rsvp.rsvpable import RSVPExtender
from collective.salesforce.rsvp.browser import forms, configuration, registration

class TestInterfaces(SFRSVPTestCase):
    
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
    
    def testClassInterfaces(self):
        """Some basic boiler plate testing of interfaces and classes"""
        self.failUnless(ISchemaExtender.implementedBy(RSVPExtender))
        self.failUnless(verifyClass(ISchemaExtender, RSVPExtender))
    
    def testContentObjectsVerify(self):
        """Some basic boiler plate testing of interfaces and content objects"""
        self.failUnless(verifyObject(interfaces.ISalesforceRSVPable, self.rsvpable))
    
    def testRegistrationFormsVerify(self):
        registration_form = self.rsvpable.restrictedTraverse('@@registration-form')
        self.failUnless(isinstance(registration_form, forms.RegistrationForm))
        self.failUnless(verifyObject(forms.IRegistrationForm, registration_form))
    
    def testBrowserViewClassInterfaces(self):
        # verify IRSVPConfigurationView
        self.failUnless(interfaces.IRSVPConfigurationView.implementedBy(configuration.RSVPConfigurationView))
        self.failUnless(verifyClass(interfaces.IRSVPConfigurationView, configuration.RSVPConfigurationView))
        
        # verify IRegistrationViewlet
        self.failUnless(interfaces.IRegistrationViewlet.implementedBy(registration.RegistrationViewlet))
        self.failUnless(verifyClass(interfaces.IRegistrationViewlet, registration.RegistrationViewlet))
        
        # verify IDynamicSFObjectFields
        self.failUnless(interfaces.IDynamicSFObjectFields.implementedBy(configuration.DynamicSFObjectFields))
        self.failUnless(verifyClass(interfaces.IDynamicSFObjectFields, configuration.DynamicSFObjectFields))
    
    def testBrowserViewObjectsVerify(self):
        # verify views are objects of the expected class, verified implementation
        rsvp_configuration = self.rsvpable.restrictedTraverse('@@rsvp-configuration')
        self.failUnless(isinstance(rsvp_configuration, configuration.RSVPConfigurationView))
        self.failUnless(verifyObject(interfaces.IRSVPConfigurationView, rsvp_configuration))
        
        sfobject_fields_configuration = self.rsvpable.restrictedTraverse('@@populateValidSFObjectFields')
        self.failUnless(isinstance(sfobject_fields_configuration, configuration.DynamicSFObjectFields))
        self.failUnless(verifyObject(interfaces.IDynamicSFObjectFields, sfobject_fields_configuration))
        
        # verify rsvp viewlet
        request = self.app.REQUEST
        context = self.rsvpable
        rsvp_viewlet = registration.RegistrationViewlet(context, request, None, None)
        self.failUnless(isinstance(rsvp_viewlet, registration.RegistrationViewlet))
        self.failUnless(verifyObject(interfaces.IRegistrationViewlet, rsvp_viewlet))
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    return suite
