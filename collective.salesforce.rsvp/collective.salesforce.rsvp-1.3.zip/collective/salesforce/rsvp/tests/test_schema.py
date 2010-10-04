import unittest

from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp.config import RSVP_SCHEMATA, RSVP_ADDL_FIELDS, \
    MAX_CAPACITY_FIELD, IS_WAITLISTABLE_FIELD, ATTENDEE_CNT_FIELD
from collective.salesforce.rsvp import interfaces

from collective.salesforce.rsvp import validators

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase

BOGUS_SF_ID = '123456789012345'

class TestSchemaExtender(SFRSVPTestCase):
    """We use archetypes.schemaextender to adapt a standard
       Archetypes schema with additional fields for configuring
       an RSVPable item within a Plone site.
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
    
    def test_schemas_untouched_prior_to_adaptation(self):
        # our content not yet marked with the marker interface
        # and therefore does not have an extended schema
        schema = self.rsvpable.Schema()
        
        for addl_field in RSVP_ADDL_FIELDS:
            self.failIf(addl_field in schema,
                'Schema %s contains %s prior to application of marker interface' % (schema, addl_field))
    
    def test_schemas_extended_with_marker(self):
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # thanks to archetypes.schemaextender, our schema now
        # contains additional fields
        schema = self.rsvpable.Schema()
        
        for addl_field in RSVP_ADDL_FIELDS:
            self.failUnless(addl_field in schema,
                'Schema %s missing %s after marker interface applied' % (schema, addl_field))
    
    def test_rsvpable_fields_in_correct_schemata(self):
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # archetypes bundles various fields into logical schemata
        # we want our Salesforce.com RSVPable fields to be bundled
        # logically together
        schema = self.rsvpable.Schema()
        rsvp_schemata_field_names = [field.getName() for field in schema.getSchemataFields(RSVP_SCHEMATA)]
        
        for addl_field in RSVP_ADDL_FIELDS:
            self.failUnless(addl_field in rsvp_schemata_field_names,
                'Schemata %s missing %s after marker interface applied' % (RSVP_SCHEMATA, addl_field))
    
    def test_sfobject_type_vocabulary_choices(self):
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # archetypes bundles various fields into logical schemata
        # we want our Salesforce.com RSVPable fields to be bundled
        # logically together
        signup_type_field = self.rsvpable.Schema().get('sfObjectSignupType')
        for sfobject in ('Contact', 'Campaign',): # some obvious object types that are bound to exist
            self.failUnless(sfobject in signup_type_field.Vocabulary(self.rsvpable).values(),
                "The vocabulary options for 'sfObjectSignupType' should include %s but does not." % sfobject)
    
    def test_sfobject_type_field_vocabulary_choices(self):
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # archetypes bundles various fields into logical schemata
        # we want our Salesforce.com RSVPable fields to be bundled
        # logically together
        sfojbect_type_field_selection_field = self.rsvpable.Schema().get('maxCapacityField')
        field_option_vocab = sfojbect_type_field_selection_field.Vocabulary(self.rsvpable)
        
        
        for sfobject_field in ('NumberOfConvertedLeads','IsActive',): # some obvious field names on the 'Campaign'
            self.failUnless(sfobject_field in field_option_vocab.keys(),
                "The vocabulary options for 'maxCapacityField' should include the field option %s but does not." % sfobject_field)
        
        for sfobject_field in ('Total Leads (NumberOfLeads)','Active (IsActive)',): # some obvious field labels on the 'Campaign'
            self.failUnless(sfobject_field in field_option_vocab.values(),
                "The vocabulary options for 'maxCapacityField' should include the field option %s but does not." % sfobject_field)

    
    def test_set_get_on_rsvpable_schema(self):
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # set rsvpable schema fields
        self.rsvpable.getField('enableCustomRegistration').set(self.rsvpable, 'custom')
        self.rsvpable.getField('customRegistration').set(self.rsvpable, self.rsvpable.UID())
        self.rsvpable.getField('sfObjectSignupType').set(self.rsvpable, 'Campaign')
        self.rsvpable.getField('sfObjectId').set(self.rsvpable, BOGUS_SF_ID)
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, 'yes')
        self.rsvpable.getField('acceptWaitlistRegistrantsField').set(self.rsvpable, IS_WAITLISTABLE_FIELD)
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD) # some possibly fictitious custom field
                                                                                         # doesn't really matter at this point
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        
        # confirm values 
        self.assertEqual('custom', self.rsvpable.getField('enableCustomRegistration').getRaw(self.rsvpable))
        self.assertEqual(self.rsvpable.UID(), self.rsvpable.getField('customRegistration').getRaw(self.rsvpable))
        self.assertEqual('Campaign', self.rsvpable.getField('sfObjectSignupType').get(self.rsvpable))
        self.assertEqual(BOGUS_SF_ID, self.rsvpable.getField('sfObjectId').get(self.rsvpable))
        self.assertEqual('yes', self.rsvpable.getField('limitRegistrationCapacity').get(self.rsvpable))
        self.assertEqual(IS_WAITLISTABLE_FIELD, self.rsvpable.getField('acceptWaitlistRegistrantsField').get(self.rsvpable))
        self.assertEqual(MAX_CAPACITY_FIELD, self.rsvpable.getField('maxCapacityField').get(self.rsvpable))
        self.assertEqual('NumberOfResponses', self.rsvpable.getField('attendeeCountField').get(self.rsvpable))
    


class FakeRequest(dict):
    def __init__(self, **kwargs):
        self.form = kwargs


class TestSchemaValidation(SFRSVPTestCase):
    """Because the various Salesforce.com RSVP relevant fields
       have some nuanced interactions with each other, we do some
       multi-field considerations for validation.
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # get base connector for use
        self.sbc = getToolByName(self.portal, 'portal_salesforcebaseconnector')
    
    def test_validation_fails_with_nonexistent_objectid(self):
        """Confirm that when a given object id of object type does not exist
           within the Salesforce.com instance, a validation error is raised
        """
        # instantiate our validator
        obj_field_validator = validators.ValidateObjectIdOfTypeExistence(self.rsvpable)
        
        # setup the request
        request = FakeRequest(sfObjectId = BOGUS_SF_ID, sfObjectSignupType = 'Campaign')
        
        # validation of our object, reveals that no object of the given id exists
        # and the user is presented with an error message and unable to save the object
        self.failUnless(obj_field_validator(request).has_key('sfObjectId'))
    
    def test_successful_validation_with_valid_objectid_of_objecttype(self):
        """Confirm that when a given object id and object type are correctly provided
           that Salesforce.com knows of one and only one relavant record
           within the given object type table.
        """
        # create a campaign for use and cleanup
        sfCampaignId = self._createCampaignForCleanup()
        
        # instantiate our validator
        obj_field_validator = validators.ValidateObjectIdOfTypeExistence(self.rsvpable)
        
        # setup the request
        request = FakeRequest(sfObjectId = sfCampaignId, sfObjectSignupType = 'Campaign')
        
        self.failIf(obj_field_validator(request))
    
    def test_validate_capacity_fields_configuration(self):
        """Confirm that we could potentially do a meaningful capacity
           check based on the relevant fields for ISalesforceRSVPable
        """
        # instantiate our validator
        cap_config_validator = validators.ValidateCapacityCheckingConfiguration(self.rsvpable)
        
        # nothing in maxCapacityField, attendeeCountField is good
        self.failIf(cap_config_validator(FakeRequest()))
        
        # something in only one of the fields is bad
        self.failUnless(cap_config_validator(FakeRequest(limitRegistrationCapacity=u'yes', maxCapacityField='', 
                                                        attendeeCountField='foo')).has_key('maxCapacityField'))
        self.failUnless(cap_config_validator(FakeRequest(limitRegistrationCapacity=u'yes', maxCapacityField='bar', 
                                                        attendeeCountField='')).has_key('attendeeCountField'))
        
        # though it doesn't matter if capacity limits are disabled
        self.failIf(cap_config_validator(FakeRequest(limitRegistrationCapacity=u'no', maxCapacityField='',
                                                     attendeeCountField='foo')))
        
        # something in both of the fields good
        self.failIf(cap_config_validator(FakeRequest(limitRegistrationCapacity=u'yes', maxCapacityField='foo', 
                                                        attendeeCountField='bar')))
        
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchemaExtender))
    suite.addTest(unittest.makeSuite(TestSchemaValidation))
    return suite
