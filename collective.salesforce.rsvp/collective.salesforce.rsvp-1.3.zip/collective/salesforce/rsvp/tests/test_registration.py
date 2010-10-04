import unittest

from DateTime import DateTime
from beatbox import SoapFaultError

from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase
from collective.salesforce.rsvp.browser import registration
from collective.salesforce.rsvp import interfaces
from collective.salesforce.rsvp.config import MAX_CAPACITY_FIELD, \
    IS_WAITLISTABLE_FIELD, ATTENDEE_CNT_FIELD


class TestRegistrationViewlet(SFRSVPTestCase):
    """Our registration viewlet is responsible for presenting a variety of
       context specific messages to the potential registrant (i.e. signup here,
       registration full, registration full, but get on the wait list).  Here
       we test the various scenarios.
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # get tools
        self.sbc = getToolByName(self.portal, 'portal_salesforcebaseconnector')
        self.utils = getToolByName(self.portal, 'plone_utils')
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # get our viewlet
        request = self.app.REQUEST
        context = self.rsvpable
        self.rsvp_viewlet = registration.RegistrationViewlet(context, request, None, None).__of__(self.rsvpable)
    
    def _invalidate_sf_cache(self):
        try:
            self.rsvp_viewlet.sf_status = None
        except AttributeError:
            pass
    
    def test_is_waitlistable(self):
        # by default, a rsvpable object shouldn't be waitlistable
        self.failIf(self.rsvp_viewlet.checkIsWaitlistable())
        
        # let's configure our rsvpable object to accept waitlist attendees
        # and ensure that our viewlet can accurately present this reality
        self.rsvpable.getField('acceptWaitlistRegistrantsField').set(self.rsvpable, IS_WAITLISTABLE_FIELD)
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self._setWaitlistableStatus(sfCampaignId, IS_WAITLISTABLE_FIELD, True)
        
        self.failUnless(self.rsvp_viewlet.checkIsWaitlistable())
    
    def test_can_outsource_registration(self):
        # by default, a rsvpable object will be configured to use the 
        # default registration form and therefore will fail
        # a test of canOutsourceRegistration
        self.failIf(self.rsvp_viewlet.canOutsourceRegistration())
        
        # let's configure our rsvpable object to provide a custom reg form
        # and ensure that our viewlet can accurately present this reality
        # we'll just use our own UID for the moment.
        self.rsvpable.getField('enableCustomRegistration').set(self.rsvpable, 'custom')
        self.rsvpable.getField('customRegistration').set(self.rsvpable, self.rsvpable.UID())
        self.failUnless(self.rsvp_viewlet.canOutsourceRegistration())
        
    def test_viewlet_provides_proper_outsourced_registration_form(self):
        # we start out with nothing
        self.failIf(self.rsvp_viewlet.outsourcedRegistrationForm())
        
        # assuming a custom registration has been set ...
        self.folder.invokeFactory('Document', 'dummy_form')
        dummy_form = self.folder.dummy_form
        # make it behave like a PFG form
        dummy_form.restrictedTraverse = lambda x: (lambda: 'dummy')
        dummy_form.getFormPrologue = dummy_form.getFormEpilogue = lambda: ''
        self.rsvpable.getField('enableCustomRegistration').set(self.rsvpable, 'custom')
        self.rsvpable.getField('customRegistration').set(self.rsvpable, dummy_form.UID())
        
        # ... and the unique id of a Salesforce.com object
        # serves as the RSVPable object...
        self.rsvpable.getField('sfObjectId').set(self.rsvpable, '0089HG_BOGUS_PLONE_TEST_CASE')
        
        # our outsourced form should have...
        outsourcedForm = self.rsvp_viewlet.outsourcedRegistrationForm()
        
        # the custom registration url
        self.assertEqual(dummy_form.absolute_url(), outsourcedForm.absolute_url())
        
        # updating the viewlet should actually render the form into rsvp_viewlet.form...
        self.rsvp_viewlet.update()
        
        # then the signup object id should be passed in the request
        self.failUnless('signup-object-id' in self.rsvp_viewlet.request.form)
        self.assertEqual(self.rsvp_viewlet.request.form['signup-object-id'], '0089HG_BOGUS_PLONE_TEST_CASE')

    def test_viewlet_is_under_capacity(self):
        # we should always start out under capacity
        self.failUnless(self.rsvp_viewlet.checkIsUnderCapacity())
        
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # configure our rsvpable event to enforce capacity
        # we start out with a very low threshold of zero
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, u'yes')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        
        # prior to setting the actual max capacity number w/in Salesforce we'll have a 
        # value that we can't cast to an integer and therefore there is no real max 
        # capacity, we ensure that our code doesn't crumple under this scenario
        self._invalidate_sf_cache()
        self.failUnless(self.rsvp_viewlet.checkIsUnderCapacity())
        
        # now we'll actually set something that can be cast to an int
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 0)
        
        # with a capacity of zero, we should definitely be
        # at capacity from the get go
        self._invalidate_sf_cache()
        self.failIf(self.rsvp_viewlet.checkIsUnderCapacity())
        
        # now we try something a bit more ambitious, we require a registration
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 1)
        
        # signups are on...
        self._invalidate_sf_cache()
        self.failUnless(self.rsvp_viewlet.checkIsUnderCapacity())
        
        # add an attendee the old fashioned way
        lead_obj = dict(type='Lead',
            FirstName = 'Ploney',
            LastName = 'McPlonesontestcase',
            Email = 'plone@mcplonesontestcase.name',
            Phone = '(555) 555-1234',
            Company = "[not provided]",  # and some required fields
            LeadSource = "Event Signup", # for the lead object
        )
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query("SELECT Id FROM Lead WHERE FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Phone = '%s'" % (
            lead_obj['FirstName'],
            lead_obj['LastName'],
            lead_obj['Email'],
            lead_obj['Phone'],))['size']
        
        # setup our lead for cleanup
        lead_res = self.sbc.create(lead_obj)
        lead_id = lead_res[0]['id']
        self._toCleanUp.append(lead_id)
        
        # create a CampaignMember junction object the old fashioned way
        cm_obj = dict(type='CampaignMember',
            LeadId = lead_id,
            CampaignId = sfCampaignId,
            Status = 'Responded',
        )
        
        cm_res = self.sbc.create(cm_obj)
        self._toCleanUp.append(cm_res[0]['id'])
        
        # with a capacity of zero, we should definitely be
        # at capacity from the get go
        self._invalidate_sf_cache()
        self.failIf(self.rsvp_viewlet.checkIsUnderCapacity())
    
    def test_viewlet_rendering(self):
        # setup a reasonable time for RSVPable object
        now = DateTime()
        self.rsvpable.setExpirationDate(now + 1)
        
        # since we're not yet tied to a Salesforce object
        # the user shouldn't see any registration capabilities
        # within our viewlet
        self.rsvp_viewlet.update()
        self.failIf(self.rsvp_viewlet.render())
        
        # once the rsvpable object is configured
        # default scenario would be to present the form,
        # since there's unlimited capacity to start
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self.rsvp_viewlet.update()
        viewlet = self.rsvp_viewlet.render()
        self.failUnless('name="rsvpform.first_name"' in viewlet)
        self.failUnless('name="rsvpform.last_name"' in viewlet)
        
        # setup an associated campaign and set the capacity to zero, set count field
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, u'yes')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 0)
        
        # with waitlisting defaulting to off, we should see...
        self.rsvp_viewlet.update()
        self.failUnless("registration is full" in self.rsvp_viewlet.render())
        
        # with a capacity of zero, but waitlists accepted, we see the form...
        self.rsvpable.getField('acceptWaitlistRegistrantsField').set(self.rsvpable, IS_WAITLISTABLE_FIELD)
        self._setWaitlistableStatus(sfCampaignId, IS_WAITLISTABLE_FIELD, True)
        self.rsvp_viewlet.update()
        viewlet = self.rsvp_viewlet.render()
        self.failUnless("added to the waitlist" in viewlet)
        self.failUnless('name="rsvpform.first_name"' in viewlet)
        
        # next we configure our own custom form...
        self.folder.invokeFactory('Document', 'dummy_form')
        dummy_form = self.folder.dummy_form
        # make it act like a PloneFormGen form
        dummy_form.restrictedTraverse = lambda x: (lambda: u'd\xfcmmy')
        dummy_form.getFormPrologue = dummy_form.getFormEpilogue = lambda: 'd\xc3\xbcmmy'
        self.rsvpable.getField('enableCustomRegistration').set(self.rsvpable, 'custom')
        self.rsvpable.getField('customRegistration').set(self.rsvpable, dummy_form.UID())
        
        # we're full, but accepting waitlist rsvps
        # the custom form should be presented to the user
        self.rsvp_viewlet.update()
        viewlet = self.rsvp_viewlet.render()
        self.failUnless("added to the waitlist" in viewlet)
        self.failUnless(u'd\xfcmmy' in viewlet)
        
        # boost the capacity to > current number of signups
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 1)
        
        # we're full, but accepting waitlist rsvps
        # the custom form should be presented to the user
        self.rsvp_viewlet.update()
        self.failUnless(u'd\xfcmmy' in self.rsvp_viewlet.render())
        
        # next we reconfigure to use default form
        self.rsvpable.getField('enableCustomRegistration').set(self.rsvpable, 'default')
        self.rsvpable.getField('customRegistration').set(self.rsvpable, None)
        
        # setting our event start/end dates to the past -- 
        # make sure we see no registration form
        self.rsvpable.setExpirationDate(now - 1.5)
        self.rsvp_viewlet.update()
        viewlet = self.rsvp_viewlet.render()
        self.failIf('name="rsvpform.first_name"' in viewlet)
        self.failIf('name="rsvpform.last_name"' in viewlet)
    
    def test_viewlet_handles_nonexistant_sfobject(self):
        # a possible scenario is that a user sets up an event
        # for rsvps and long after the event forgets about the lingering
        # relationship between campaign and salesforce.com object and
        # subsequently deletes the campaign from salesforce.com
        # does the registration viewlet handle this scenario gracefully
        # unlikely though it may be...
        
        # some reasonable configuration to the plone content object
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, u'yes')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        
        # ... after sometime, we directly delete the associated campaign from Salesforce.com
        # and remove it from the to be deleted list upon test case cleanup
        self.sbc.delete([sfCampaignId,])
        self._toCleanUp.remove(sfCampaignId)
        
        # we shouldn't have any capacity
        self.assertEqual(None, self.rsvp_viewlet.checkIsUnderCapacity())
        
        # ... and we shouldn't be getting anything
        # back from our viewlet's rendering ...
        self.rsvp_viewlet.update()
        self.failIf(self.rsvp_viewlet.render())
    
    def test_viewlet_handles_misconfiguration_of_capacity_fields(self):
        # a user could choose a field that represents the attendeeCountField
        # or the maxCapacityField, but not both together.  Since these are
        # used to suggest current event capacities in conjunction, even
        # though the user should see validation, we want to make sure
        # we're covered for this situation.
        # some reasonable configuration to the plone content object
        self._configureRSVPableObject(self.rsvpable)
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, u'yes')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        # ^^^ notice the lack of attendeeCountField...
        
        # in this scenario, we can't develop an opinion about capacity
        # so we we'll let in registrants in
        self.failUnless(self.rsvp_viewlet.checkIsUnderCapacity())
        
        # and the converse ...
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, '')
        # ^^^ notice the unsetting of maxCapacityField
        
        # we should still let registrants in
        self._invalidate_sf_cache()
        self.failUnless(self.rsvp_viewlet.checkIsUnderCapacity())
        
        # finally, what about a bogus field or one that was configured and then deleted
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, 'MyBogusAttendeeCountFieldThatWasDeleted__c')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        
        # in this case we'll let the exception show
        self._invalidate_sf_cache()
        self.assertRaises(SoapFaultError, self.rsvp_viewlet.checkIsUnderCapacity)
    
    def test_registration_viewlet_post_registration(self):
        pass


class TestDefaultRegistrationForm(SFRSVPTestCase):
    """Our product provides a default registration form implementing the
       obvious scenario of creating a brand new lead object and the lead/campaign
       junction object with the appropriate unique id of the created lead and
       the chosen unique id provided by the contextual rsvpable object.  In most
       cases, folks will be using PloneFormGen with the Salesforce PFG Adapter which
       gives pretty complete control over the entire registration process and it's 
       communication with Salesforce.com.  Salesforce PFG Adapter and its ilk 
       aren't explicit dependencies though.
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
        
        # get our viewlet
        request = self.app.REQUEST
        context = self.rsvpable
        self.rsvp_viewlet = registration.RegistrationViewlet(context, request, None, None).__of__(self.rsvpable)
    
    def _invalidate_sf_cache(self):
        try:
            self.rsvp_viewlet.sf_status = None
        except AttributeError:
            pass
    
    def test_registration_incomplete_data(self):
        # setup an incomplete request that will fail validation
        incomplete_request = TestRequest(form={'rsvpform.first_name':u'John',
                                               'rsvpform.last_name':u'',
                                               'rsvpform.actions.register':'Register'})
        incomplete_request.RESPONSE = incomplete_request.response
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, incomplete_request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        self.failUnless(u'message_registration_failed' in registration_form.status)
    
    def test_registration_email_invariant(self):
        # setup an incomplete request that will fail validation
        invalid_email_request = TestRequest(form={'rsvpform.first_name':'Ploney',
                                    'rsvpform.last_name':'McPlonesontestcase',
                                    'rsvpform.email':'this is not a valid email address',
                                    'rsvpform.company':'Plone RSVP Test Case Organization',
                                    'rsvpform.phone':'(555) 555-1234',
                                    'rsvpform.actions.register':'Register'})
        invalid_email_request.RESPONSE = invalid_email_request.response
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, invalid_email_request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        self.failUnless(u'message_registration_failed' in registration_form.status)

    def test_bait_n_switch_signup_form_after_registration_overage(self):
        """ make sure capacity is checked when submitting the form, not
            just when rendering it initially
        """

        # configure our object and tie it to a campaign for rsvps
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)

        # we setup a capacity of 1 and take the default of no waitlisting
        self.rsvpable.getField('limitRegistrationCapacity').set(self.rsvpable, u'yes')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 1)

        # the user "checks" whether they can still register on page load
        self.failUnless(self.rsvp_viewlet.checkIsUnderCapacity())

        # but at the same time another user registers. we don't 
        # care how, so we add an attendee the old fashioned way
        lead_obj = dict(type='Lead',
            FirstName = 'Ploney',
            LastName = 'McPlonesontestcase',
            Email = 'plone@mcplonesontestcase.name',
            Phone = '(555) 555-1234',
            Company = "[not provided]",  # and some required fields
            LeadSource = "Event Signup", # for the lead object
        )

        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query("SELECT Id FROM Lead WHERE FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Phone = '%s'" % (
            lead_obj['FirstName'],
            lead_obj['LastName'],
            lead_obj['Email'],
            lead_obj['Phone'],))['size']

        # setup our lead for cleanup
        lead_res = self.sbc.create(lead_obj)
        lead_id = lead_res[0]['id']
        self._toCleanUp.append(lead_id)

        # create a CampaignMember junction object the old fashioned way
        cm_obj = dict(type='CampaignMember',
            LeadId = lead_id,
            CampaignId = sfCampaignId,
            Status = 'Responded',
        )

        cm_res = self.sbc.create(cm_obj)
        self._toCleanUp.append(cm_res[0]['id'])

        # now if we were to talk to the viewlet again, 
        # we we wouldn't be encouraged to register ...
        self._invalidate_sf_cache()
        self.failIf(self.rsvp_viewlet.checkIsUnderCapacity())
        # ... but of course we can still fill out the already loaded form and we do
        too_late_request = TestRequest(form={'rsvpform.first_name':'TestCaseTooLate',
                                    'rsvpform.last_name':'RSVP-Registrant',
                                    'rsvpform.email':'plone@testcasetoolateregistrant.name',
                                    'rsvpform.actions.register':'Register'})
        too_late_request.RESPONSE = too_late_request.response
        self.rsvp_viewlet = registration.RegistrationViewlet(self.rsvpable, too_late_request, None, None).__of__(self.rsvpable)
        too_late_query = self.sbc.query("SELECT Id FROM Lead WHERE FirstName = '%s' AND LastName = '%s' AND Email = '%s'" % (
            too_late_request.form['rsvpform.first_name'],
            too_late_request.form['rsvpform.last_name'],
            too_late_request.form['rsvpform.email'],))
        # just in case we're destined for failure, we get ready to cleanup
        if len(too_late_query['records']):
            self._toCleanUp.append(too_late_query['records'][0]['Id'])

        # but fortunately our action validation saves the day and doesn't
        # allow the registration to go through...
        self.rsvp_viewlet.update()
        self.failIf(self.rsvp_viewlet.isUnderCapacity)
        self.assertEqual(0, too_late_query['size'])

    def test_successful_registration_interaction_with_salesforce(self):
        # setup a reasonable request
        request = TestRequest(form={'rsvpform.first_name':'Ploney',
                                    'rsvpform.last_name':'McPlonesontestcase',
                                    'rsvpform.email':'plone@mcplonesontestcase.name',
                                    'rsvpform.company':'Plone RSVP Test Case Organization',
                                    'rsvpform.phone':'(555) 555-1234',
                                    'rsvpform.actions.register':'Register'})
        request.RESPONSE = request.response
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query("SELECT Id FROM Lead WHERE FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Company = '%s' AND Phone = '%s'" % (
            request.form['rsvpform.first_name'],
            request.form['rsvpform.last_name'],
            request.form['rsvpform.email'],
            request.form['rsvpform.company'],
            request.form['rsvpform.phone'],))['size']
        
        # configure our object and tie it to a campaign for rsvps
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        
        # get ready to cleanup after ourselves
        lead_res = self.sbc.query("SELECT Id, FirstName, LastName, Email, "
                                  "Company, Phone FROM Lead WHERE FirstName = "
                                  "'%s' AND LastName = '%s' AND Email = '%s' "
                                  "AND Company = '%s' AND Phone = '%s'" % (
            request.form['rsvpform.first_name'],
            request.form['rsvpform.last_name'],
            request.form['rsvpform.email'],
            request.form['rsvpform.company'],
            request.form['rsvpform.phone'],))
        
        lead_id = lead_res['records'][0]['Id']
        self._toCleanUp.append(lead_id)
        
        # get the junction object
        junc_res = self.sbc.query("SELECT LeadId, CampaignId, Id FROM CampaignMember WHERE CampaignId = '%s' AND LeadId = '%s'" % (sfCampaignId, lead_id))
        self._toCleanUp.append(junc_res['records'][0]['Id'])
        
        # with that simple form completion, we want to see ...
        ## one newly created lead object
        self.assertEqual(1, lead_res['size'])
        self.assertEqual(request.form['rsvpform.first_name'], lead_res['records'][0]['FirstName'])
        self.assertEqual(request.form['rsvpform.last_name'], lead_res['records'][0]['LastName'])
        self.assertEqual(request.form['rsvpform.email'], lead_res['records'][0]['Email'])
        self.assertEqual(request.form['rsvpform.company'], lead_res['records'][0]['Company'])
        self.assertEqual(request.form['rsvpform.phone'], lead_res['records'][0]['Phone'])
        
        # one CampaignMember junction object, w/ appropriate LeadId and 
        self.assertEqual(1, junc_res['size'])
        self.assertEqual(sfCampaignId, junc_res['records'][0]['CampaignId'])
        self.assertEqual(lead_id, junc_res['records'][0]['LeadId'])
        
        # and with that, a lead associated with our campaign
        # we look at NumberOfLeads, rather than NumberOfResponses b/c
        # the default CampaignMemberStatus for a Campaign is sent
        campaign_res = self.sbc.retrieve(['NumberOfLeads',],'Campaign',[sfCampaignId,])
        self.assertEqual(1, campaign_res[0]['NumberOfLeads'])
    
    def test_registration_without_optional_fields(self):
        """Confirms optional fields are actually optional"""
        # setup a reasonable request w/out optional fields included
        request = TestRequest(form={'rsvpform.first_name':'Ploney',
                                    'rsvpform.last_name':'McPlonesontestcase',
                                    'rsvpform.email':'plone@mcplonesontestcase.name',
                                    'rsvpform.actions.register':'Register'})
        request.RESPONSE = request.response
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query("SELECT Id FROM Lead WHERE FirstName = '%s' AND LastName = '%s' AND Email = '%s'" % (
            request.form['rsvpform.first_name'],
            request.form['rsvpform.last_name'],
            request.form['rsvpform.email'],))['size']
        
        # configure our object and tie it to a campaign for rsvps
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        
        # get ready to cleanup after ourselves
        lead_res = self.sbc.query("SELECT Id, FirstName, LastName, Email, Company, Phone FROM Lead WHERE FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Company = '[not provided]' AND Phone = ''" % (
            request.form['rsvpform.first_name'],
            request.form['rsvpform.last_name'],
            request.form['rsvpform.email'],))
        
        lead_id = lead_res['records'][0]['Id']
        self._toCleanUp.append(lead_id)
        
        # get the junction object
        junc_res = self.sbc.query("SELECT LeadId, CampaignId, Id FROM CampaignMember WHERE CampaignId = '%s' AND LeadId = '%s'" % (sfCampaignId, lead_id))
        self._toCleanUp.append(junc_res['records'][0]['Id'])
        
        # with that simple form completion, we want to see ...
        ## one newly created lead object
        self.assertEqual(1, lead_res['size'])
        self.assertEqual(request.form['rsvpform.first_name'], lead_res['records'][0]['FirstName'])
        self.assertEqual(request.form['rsvpform.last_name'], lead_res['records'][0]['LastName'])
        self.assertEqual(request.form['rsvpform.email'], lead_res['records'][0]['Email'])
        self.assertEqual("[not provided]", lead_res['records'][0]['Company'])
        
        # one CampaignMember junction object, w/ appropriate LeadId and 
        self.assertEqual(1, junc_res['size'])
        self.assertEqual(sfCampaignId, junc_res['records'][0]['CampaignId'])
        self.assertEqual(lead_id, junc_res['records'][0]['LeadId'])
        
        # and with that, a lead associated with our campaign
        # we look at NumberOfLeads, rather than NumberOfResponses b/c
        # the default CampaignMemberStatus for a Campaign is sent
        campaign_res = self.sbc.retrieve(['NumberOfLeads',],'Campaign',[sfCampaignId,])
        self.assertEqual(1, campaign_res[0]['NumberOfLeads'])
    


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegistrationViewlet))
    suite.addTest(unittest.makeSuite(TestDefaultRegistrationForm))
    return suite
