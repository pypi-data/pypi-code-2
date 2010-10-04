import unittest
from zope.interface import alsoProvides

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase
from collective.salesforce.rsvp import interfaces
from collective.salesforce.rsvp.browser import configuration
from collective.salesforce.rsvp.config import ATTENDEE_CNT_FIELD, LIMIT_CAPACITY_HIDABLE

class TestRSVPConfiguration(SFRSVPTestCase):
    """Test the enabling and disabling of RSVP functionality
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # get our configuration view
        self.rsvp_configuration = self.rsvpable.restrictedTraverse("@@rsvp-configuration")
    
    def testIsRSVPEnabled(self):
        # prior to applying the marker interface our content object
        # should fail an isRSVPEnabled check
        self.failIf(self.rsvp_configuration.isRSVPEnabled())
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # now isRSVPEnabled check should return a true value
        self.failUnless(self.rsvp_configuration.isRSVPEnabled())
    
    def testEnableRSVP(self):
        # to start, we don't provide the interface
        self.failIf(interfaces.ISalesforceRSVPable.providedBy(self.rsvpable))
        
        # via our configuration view, enable rsvp on the context of self.rsvpable
        self.rsvp_configuration.enableRSVPs()
        
        # our object should now provide the interface
        self.failUnless(interfaces.ISalesforceRSVPable.providedBy(self.rsvpable))
    
    def testDisableRSVP(self):
        # manually apply the marker interface to our event object
        # remember, we're aiming to test disableRSVPs in isolation
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # our object should provide the interface
        self.failUnless(interfaces.ISalesforceRSVPable.providedBy(self.rsvpable))
        
        # via our configuration view, enable rsvp on the context of self.rsvpable
        self.rsvp_configuration.disableRSVPs()
        
        # assuming disableRSVPs was successful, we no longer provide the interface
        self.failIf(interfaces.ISalesforceRSVPable.providedBy(self.rsvpable))
    

class TestRSVPConfigurationInteractivity(SFRSVPTestCase):
    """Tests code backing the kss interactivity present within
       the RSVP configuration editing interface.
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
    
    def test_toggle_available_field_options(self):
        # get our configuration view
        rsvp_configuration = configuration.DynamicSFObjectFields(self.rsvpable, self.app.REQUEST)
        
        # inspect the campaign dropdown html
        campaign_option_dropdown = rsvp_configuration.toggle_available_field_options('Campaign')
        num_leads_str = """<option value="NumberOfConvertedLeads">Converted Leads (NumberOfConvertedLeads)</option>"""
        self.failUnless(num_leads_str in campaign_option_dropdown)
        
        # ensure we have a blank option before other options
        blank_default_str = """<option value="" selected="selected">"""
        self.failUnless(campaign_option_dropdown.index(num_leads_str) > campaign_option_dropdown.index(blank_default_str))
        
        event_field_option = """<option value="DurationInMinutes">Duration (DurationInMinutes)</option>"""
        kss_updated_html = rsvp_configuration.toggle_available_field_options('Event')
        # now do the same for the event dropdown html
        self.failUnless(event_field_option in kss_updated_html)
        # this should happen in 3 places on the page, make sure that's true
        self.assertEqual(3, kss_updated_html.count(event_field_option))
    
    def test_toggle_available_field_options_properer_stringifies_options(self):
        """We're casting a list of options to a string which produces html like:
             '<select name="..." id="...">[\'<option value=""
           
           We really want to see something like the following, which suggests
           that the list has been appropriately joined:
             '<select name="..." id="...">\n\t<option value="" ...
           
           The above issue is presenting problems in Plone 3.0.6, which is throwing
           a bunch of options like the following into the select list:
                [
                '\'
                ]
                
           See: http://plone.org/products/collective.salesforce.rsvp/issues/1
        """
        # get our configuration view
        rsvp_configuration = configuration.DynamicSFObjectFields(self.rsvpable, self.app.REQUEST)
        
        # inspect the campaign dropdown html
        event_option_dropdown = rsvp_configuration.toggle_available_field_options('Event')
        unwanted_str_repr_list = """[\'<option value="""""
        self.failIf(unwanted_str_repr_list in event_option_dropdown)
    
    def test_custom_form_widget_visibility_on_load(self):
        # get our configuration view
        rsvp_configuration = configuration.DynamicSFObjectFields(self.rsvpable, self.app.REQUEST)
        
        # default state uses default form, so we should hide the custom form chooser widget
        current_val = self.rsvpable.getField('enableCustomRegistration').get(self.rsvpable)
        self.assertEquals(u'default', current_val)
        returned_command = rsvp_configuration.hide_custom_form_selector_if_inactive()
        self.assertTrue('selector="#archetypes-fieldname-customRegistration"' in returned_command)
        self.assertTrue('name="addClass"' in returned_command)
        self.assertTrue('param name="value">hiddenStructure' in returned_command)
        
        # set the rsvpable to use a custom form
        self.rsvpable.getField('enableCustomRegistration').set(self.rsvpable, u'custom')
        
        # now we shouldn't hide anything
        current_val = self.rsvpable.getField('enableCustomRegistration').get(self.rsvpable)
        self.assertEquals(u'custom', current_val)
        returned_command = rsvp_configuration.hide_custom_form_selector_if_inactive()
        self.assertEquals('', returned_command)
    
    def test_toggle_capacity_field_visibility(self):
        # get our configuration view
        rsvp_configuration = configuration.DynamicSFObjectFields(self.rsvpable, self.app.REQUEST)
        
        # make sure that we're adding the hiddenStructure class if no capacity 
        # limits are needed and we want to do this on multiple fields
        returned_disable_command = rsvp_configuration.toggle_capacity_fields_visibility(formvar='no')
        self.assertEquals(len(LIMIT_CAPACITY_HIDABLE), returned_disable_command.count('name="addClass"'))
        self.assertEquals(len(LIMIT_CAPACITY_HIDABLE), returned_disable_command.count('param name="value">hiddenStructure'))
        
        # make sure that we're removing the hiddenStructure class if no capacity 
        # limits are needed and we want to do this on multiple fields
        returned_enable_command = rsvp_configuration.toggle_capacity_fields_visibility(formvar='yes')
        self.assertEquals(len(LIMIT_CAPACITY_HIDABLE), returned_enable_command.count('name="removeClass"'))
    
    def test_capacity_field_widgets_visibility_on_load(self):
        # get our configuration view
        rsvp_configuration = configuration.DynamicSFObjectFields(self.rsvpable, self.app.REQUEST)
        
        # default state uses default form, so we should hide the custom form chooser widget
        current_val = self.rsvpable.getField('limitRegistrationCapacity').get(self.rsvpable)
        self.assertEquals(u'no', current_val)
        returned_command = rsvp_configuration.hide_capacity_selectors_if_inactive()
        for selector in LIMIT_CAPACITY_HIDABLE:
            self.assertTrue('selector="#archetypes-fieldname-%s"' % selector in returned_command)
        
        self.assertEquals(len(LIMIT_CAPACITY_HIDABLE), returned_command.count('name="addClass"'))
        self.assertEquals(len(LIMIT_CAPACITY_HIDABLE), returned_command.count('param name="value">hiddenStructure'))
        
        # set the rsvpable to use a custom form
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, u'yes')
        
        # now we shouldn't hide anything
        current_val = self.rsvpable.getField('limitRegistrationCapacity').get(self.rsvpable)
        self.assertEquals(u'yes', current_val)
        returned_command = rsvp_configuration.hide_capacity_selectors_if_inactive()
        self.assertEquals('', returned_command)
    
    def test_previously_curr_values_pre_selected_upon_toggle(self):
        # setup a reasonable attendee total field on our object
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        
        # get our configuration view
        rsvp_configuration = configuration.DynamicSFObjectFields(self.rsvpable, self.app.REQUEST)
        # our previously chosen value should be selected
        campaign_option_dropdown = rsvp_configuration.toggle_available_field_options('Campaign')
        num_leads_str = """<option value="NumberOfResponses" selected="selected">"""
        self.failUnless(num_leads_str in campaign_option_dropdown)
        self.assertEqual(1, campaign_option_dropdown.count(num_leads_str))
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRSVPConfiguration))
    suite.addTest(unittest.makeSuite(TestRSVPConfigurationInteractivity))
    return suite
