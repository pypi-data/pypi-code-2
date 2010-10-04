PROJECTNAME = 'collective.salesforce.rsvp'

## RSVP field schemata
RSVP_SCHEMATA = 'RSVP'

## RSVP additional fields
RSVP_ADDL_FIELDS = ('enableCustomRegistration','customRegistration','sfObjectSignupType',
                    'sfObjectId','limitRegistrationCapacity','maxCapacityField','attendeeCountField',
                    'acceptWaitlistRegistrantsField',)

## These fields are hidden and revealed with KSS when limitRegistrationCapacity is toggled
## they also happen to be the fields that are select lists based on the chosen SFObject Type
## if at any point the overloading of this list become undesirable, it's fine to split this
## into multiple field lists
LIMIT_CAPACITY_HIDABLE = OBJ_FIELD_SELECT_LISTS = (
    'attendeeCountField', 
    'maxCapacityField', 
    'acceptWaitlistRegistrantsField',)

## Default Max Capacity field (used in test suite)
MAX_CAPACITY_FIELD = 'Max_Capacity__c'

## Default field representing current signup count (used in test suite)
ATTENDEE_CNT_FIELD = 'NumberOfResponses'

## Default Waitlistable field (used in test suite)
IS_WAITLISTABLE_FIELD = 'Allow_Waitlists__c'

