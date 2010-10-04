from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IObjectPostValidation

from collective.salesforce.rsvp import RSVPMessageFactory as _
from collective.salesforce.rsvp.interfaces import ISalesforceRSVPable

# This is a subscription adapter which is used to validate the existence
# of a Salesforce.com object id of the chosen Salesforce.com object type
# It will be called after the normal schema validation.
class ValidateObjectIdOfTypeExistence(object):
    """Validate that an object id of the chosen 
       object type truly exists.
    """
    implements(IObjectPostValidation)
    adapts(ISalesforceRSVPable)
    
    obj_id_field_name = 'sfObjectId'
    obj_type_field_name = 'sfObjectSignupType'
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, request):
        obj_id = request.form.get(self.obj_id_field_name, request.get(self.obj_id_field_name, None))
        obj_type = request.form.get(self.obj_type_field_name, request.get(self.obj_type_field_name, None))
        
        if obj_id and obj_type: # we'll catch missing field values through other validation mechanisms
            sbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
            res = sbc.query("SELECT Id FROM %s WHERE Id='%s'" % (obj_type, obj_id))
            num_results = res['size']
            
            if num_results == 0:
                return {self.obj_id_field_name : _(u'message_sf_object_missing',
                                                   default=u"There must be exactly one object of type ${obj_type} "
                                                            "with the id ${obj_id} within your Salesforce.com instance "
                                                            "for RSVP capabilities.",
                                                   mapping={'obj_type': obj_type, 'obj_id': obj_id})}
        
        # Returning None means no error
        return None

# This is a subscription adapter which is used to validate the
# presence of both a maxCapacityField and an attendeeCountField
# or neither, since in conjunction they work to suggest 
# underage/overage of an events current capacity and they're 
# rather useless in isolation, so we take this opportunity to
# warn the user about their poor configuration choices.
class ValidateCapacityCheckingConfiguration(object):
    """Validate that capacity checking fields are 
       correctly configured.
    """
    implements(IObjectPostValidation)
    adapts(ISalesforceRSVPable)
    
    is_capacity_limited_field_name = 'limitRegistrationCapacity'
    max_cap_field_name = 'maxCapacityField'
    attendee_count_field_name = 'attendeeCountField'
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, request):
        isCapacityLimited = request.form.get(self.is_capacity_limited_field_name, request.get(self.is_capacity_limited_field_name, None))
        cap_val = request.form.get(self.max_cap_field_name, request.get(self.max_cap_field_name, None))
        cnt_val = request.form.get(self.attendee_count_field_name, request.get(self.attendee_count_field_name, None))

        if isCapacityLimited != u'yes':
            # pass validation if capacity limits are disabled
            return None
        
        if cap_val and cnt_val or not cap_val and not cnt_val:
            # Returning None means no error
            return None
        else:
            if cap_val:
                return {self.attendee_count_field_name : _(u'message_missing_attendee_count_field',
                                                           default=u"You've added a value for the 'Maximum Capacity Field', \
                                                             but not the 'Attendee Count Field'.  Without this, we cannot \
                                                             calculate the current room for additional attendees.  Either \
                                                             clear the value for 'Maximum Capacity Field' or choose a \
                                                             value for the 'Attendee Count Field'.")}
            if cnt_val:
                return {self.max_cap_field_name : _(u'message_missing_max_capacity_field',
                                                    default=u"You've added a value for the 'Attendee Count Field', \
                                                      but not the 'Maximum Capacity Field'.  Without this, we cannot \
                                                      calculate the current room for additional attendees.  Either \
                                                      clear the value for 'Attendee Count Field' or choose a \
                                                      value for the 'Maximum Capacity Field'.")}
        
