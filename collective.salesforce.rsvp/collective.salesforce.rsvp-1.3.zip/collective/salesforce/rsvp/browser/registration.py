from zope.interface import implements
from ZPublisher.Publish import Retry
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.salesforce.rsvp.interfaces import IRegistrationViewlet

class RegistrationViewlet(ViewletBase):
    """See ..interfaces/IRegistrationViewlet
    """
    implements(IRegistrationViewlet)
    
    index = ViewPageTemplateFile('templates/registration-viewlet.pt')
    def render(self):
        return self.index()

    def __init__(self, context, request, view, manager):
        super(RegistrationViewlet, self).__init__(context, request, view, manager)
        self.sbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
        self.utils = getToolByName(self.context, 'plone_utils')
        self.sf_status = None

    def update(self):
        # clear cache of attributes looked up from SF
        self.sf_status = None
        
        self.isWaitlistable = self.checkIsWaitlistable()
        self.isUnderCapacity = self.checkIsUnderCapacity()
        self.isAvailable = self.checkIsAvailable()
        
        self.isCompleted = False
        if self.canOutsourceRegistration():
            # pre-render the form so we can determine whether it's completed or not
            # -- but ONLY if we are under capacity or have a waitlist, because rendering
            # the form may have the side effect of doing a registration
            # (this works because if the campaign is over capacity and not waitlistable
            # then the value of isCompleted doesn't matter -- we show a 'full' message
            # either way)
            if self.isUnderCapacity or self.isWaitlistable:
                self.form = self.renderOutsourcedForm()
            else:
                self.form = ''
        else:
            self.form = self.context.restrictedTraverse("@@registration-form")
            self.form.update()
            if self.form.status and u'message_registration_received' in self.form.status:
                self.isCompleted = True
    
    def renderOutsourcedForm(self):
        # inject the SF object id into the request so it can be used by a
        # embedded PFG form
        self.request.form['signup-object-id'] = self.associated_sfobject_id
        
        form = self.outsourcedRegistrationForm()
        form_view = self.outsourcedRegistrationForm().restrictedTraverse('@@embedded')
        form_view.prefix = u'rsvp'
        try:
            out = form_view()
            if isinstance(out, unicode):
                out = out.encode('utf8')
            return form.getFormPrologue() + out + form.getFormEpilogue()
        except Retry:
            # embedded PFG forms raise Retry instead of traversing to a thank you page
            if 'fg_result_view' in self.request._orig_env['PATH_INFO']:
                # default if no thank you page is provided -- let's intercept it
                self.isCompleted = True
                # doesn't matter if we return an empty string because the completion
                # message will be shown instead
                return ''
            else:
                # pass the exception through so we load the different thank you page
                raise
    
    def render_form(self):
        if self.canOutsourceRegistration():
            if self.form:
                # pre-rendered HTML from update method
                return self.form
            else:
                return self.renderOutsourcedForm()
        else:
            return self.form.render()

    @property
    def associated_sfobject_id(self):
        return self.context.getField('sfObjectId').get(self.context)

    @property
    def sfobject_signup_type(self):
        return self.context.getField('sfObjectSignupType').get(self.context)

    def _retrieveRSVPableSettings(self):
        if self.sf_status:
            return self.sf_status
            
        requested_fields = []
        possible_fields = ('acceptWaitlistRegistrantsField', 'maxCapacityField', 'attendeeCountField')
        for field in possible_fields:
            field_id = self.context.getField(field).get(self.context)
            if field_id:
                requested_fields.append(field_id)
        
        self.sf_status = self.sbc.retrieve(
            requested_fields, 
            self.sfobject_signup_type, 
            [self.associated_sfobject_id,])
        return self.sf_status
    
    def checkIsAvailable(self):
        """ Returns true if the viewlet should be shown
        """
        # in order to get into our registration related options, the following must be true:
        #  1) an expiration date that's either none or in the future (since we're talking 
        #     AT-objects here and everything using this should have that) 
        #  2) a Salesforce.com object id exists
        #  3) self.isUnderCapacity() is not None, which would signify that an item has been removed
        
        if (self.context.getExpirationDate() is not None and not self.context.getExpirationDate().isFuture()):
            return False
            
        if not self.associated_sfobject_id:
            return False
            
        if self.isUnderCapacity is None:
            return False
        
        return True
        
    def checkIsWaitlistable(self):
        """See ..interfaces/IRegistrationViewlet
        """
        waitlistable_field = self.context.getField('acceptWaitlistRegistrantsField').get(self.context)
        
        if waitlistable_field:
            # it's worth inspecting salesforce.com to determine waitlistability
            waitlistable_status_res = self._retrieveRSVPableSettings()
            
            # The criteria for accepting waitlist applications are:
            #   1) we have exactly one item from Salesforce.com for the id
            #   2) the resulting item value is of boolean type
            #   3) the resulting item value is actually true
            if len(waitlistable_status_res) == 1 and \
               type(waitlistable_status_res[0][waitlistable_field]) == type(bool()) and \
               waitlistable_status_res[0][waitlistable_field] is True:
                return True
        
        return False
    
    def checkIsUnderCapacity(self):
        """See ..interfaces/IRegistrationViewlet
        """
        isCapacityLimited = self.context.getField('limitRegistrationCapacity').get(self.context)
        maxCapacityField = self.context.getField('maxCapacityField').get(self.context)
        attendeeCountField = self.context.getField('attendeeCountField').get(self.context)
        
        # if we don't have this stuff, don't even bother trying to figure it out
        if isCapacityLimited == u'yes' and maxCapacityField and attendeeCountField:
            # we need to get the max capacity value, we'll also 
            # get the attendee count value while we're at it
            rsvp_status_res = self._retrieveRSVPableSettings()
            
            # the object may no longer exist
            if len(rsvp_status_res) == 1:
                # we have an item, so we can move along
                pass
            else:
                # the salesforce object no longer exists
                # so there's no concept of capacity
                # we return and test for none in this scenario
                return None
            
            try:
                if int(rsvp_status_res[0][maxCapacityField]) == 0:
                    # never was any capacity
                    return False
            except TypeError:
                # can't convert max value to int for comparison
                # must still have room for rsvps
                return True
            
            # we've delayed long enough, get into the rigors of checking capacity
            currAttendeeNum = rsvp_status_res[0][attendeeCountField]
            
            if int(currAttendeeNum) >= int(rsvp_status_res[0][maxCapacityField]):
                return False
                
        return True
    
    def canOutsourceRegistration(self):
        """See ..interfaces/IRegistrationViewlet
        """
        if  self.context.getField('enableCustomRegistration').get(self.context) == 'custom' and \
            self.context.getField('customRegistration').getRaw(self.context):
            return True
        
        return False
    
    def outsourcedRegistrationForm(self):
        """See ..interfaces/IRegistrationViewlet
        """
        if self.canOutsourceRegistration():
            # we first assume a UID
            uid_cat = getToolByName(self.context, 'uid_catalog')
            results = uid_cat.searchResults(
                UID = self.context.getField('customRegistration').getRaw(self.context),
            )
            if len(results):
                return results[0].getObject()
        else:
            return None
