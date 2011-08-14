# -*- coding: utf-8 -*-
# $Id: ECLecture.py 1571 2011-08-10 17:44:43Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = 'Mario Amelung <mario.amelung@gmx.de>'
__docformat__ = 'plaintext'

#import re
#import urllib
import interfaces
from types import StringType, IntType
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import Schema, DisplayList, registerType
from Products.Archetypes.atapi import StringField, LinesField, DateTimeField, \
    IntegerField, TextField
from Products.Archetypes.atapi import StringWidget, LinesWidget, \
    CalendarWidget, SelectionWidget, TextAreaWidget, RichWidget

from Products.CMFCore import permissions

from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget


from Products.ECLecture import config
from Products.ECLecture import LOG
from Products.ECLecture import ECMessageFactory as _
from Products.ECLecture.content.TimePeriodField import TimePeriodField

try:
    from Products.ECAssignmentBox.content.ECFolder import ECFolder as SuperClass
    from Products.ECAssignmentBox.content.ECFolder import ECFolder_schema as SuperSchema
except:
    LOG.debug('Import failed: Products.ECAssignmentBox.content.ECFolder')
    from Products.ATContentTypes.content.folder import ATFolder as SuperClass
    from Products.ATContentTypes.content.folder import ATFolderSchema as SuperSchema


NO_RECURRENCE = "0"
DAILY = "1"
WEEKLY = "2"
MONTHLY = "3"
YEARLY = "4"

NO_GROUP = ""


schema = Schema((

    StringField('courseType',
        required = False,
        widget = StringWidget(
            label = "Course type",
            description = "Enter the type of this course (e.g., Lecture or Lab Exercise)",
            label_msgid = 'label_course_type',
            description_msgid = 'help_course_type',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    LinesField('instructors',
        required = True,
        languageIndependent = True,
        searchable = True,
        widget = LinesWidget(
            label = "Instructors",
            description = "User names or names of instructors, one per line",
            label_msgid = 'label_instructors',
            description_msgid = 'help_instructors',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    TimePeriodField('timePeriod',
        accessor = 'getTimePeriod',
        edit_accessor = 'getTimePeriodForEdit',
        required = True,
        default = ['11:00', '13:00'],
        widget = StringWidget(
            macro = 'time_period',
            size = 5,
            maxlength = 5,
            label = "Time period",
            description = "Start and end times of this course",
            label_msgid = 'label_time_period',
            description_msgid = 'help_time_period',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    DateTimeField('startDate',
        required = True,
        widget = CalendarWidget(
            label = "Start date",
            description = "First regular date",
            label_msgid = 'label_start_date',
            description_msgid = 'help_start_date',
            show_hm = False, 
            #show_ymd = True,
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),
    
    DateTimeField('endDate',
        required = True,
        widget = CalendarWidget(
            label = "End date",
            description = "Last regular date",
            label_msgid = 'label_end_date',
            description_msgid = 'help_end_date',
            show_hm = False, 
            #show_ymd = True,
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),
                                                   
    StringField('recurrence',
        required = True,
        vocabulary = 'getRecurrenceDisplayList',
        default = WEEKLY,
        widget = SelectionWidget(
            format = "radio", # possible values: flex, select, radio
            label = "Recurrence",
            description = "How often this course takes place",
            label_msgid = 'label_recurrence',
            description_msgid = 'help_recurrence',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),
                                                   
    DateTimeField('firstSession',
        widget = CalendarWidget(
            label = "First session",
            description = "Date for the first session for this course",
            label_msgid = 'label_first_session',
            description_msgid = 'help_first_session',
            #show_hm = False, 
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    StringField('location',
        required = True,
        widget = StringWidget(
            label = "Location",
            description = "Location for this course",
            label_msgid = 'label_location',
            description_msgid = 'help_location',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    StringField('courseLanguage',
        vocabulary = 'getLanguagesDL',
        widget = SelectionWidget(
            label = 'Language of instruction',
            description = 'The language used for teaching this course',
            label_msgid = 'label_course_language',
            description_msgid = 'help_course_language',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    StringField('credits',
        required = False,
        widget = StringWidget(
            label = "Credits",
            description = "Credits which can be gained in this course",
            label_msgid = 'label_credits',
            description_msgid = 'help_credits',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    TextField('prereq',
        required = False,
        default_content_type = config.DEFAULT_CONTENT_TYPE,
        default_output_type = config.DEFAULT_OUTPUT_TYPE,
        allowable_content_types = config.ALLOWED_CONTENT_TYPES,
        widget = TextAreaWidget(
            label = "Prerequisites",
            description = "Describe which prerequisites are required for this course",
            label_msgid = 'label_prereq',
            description_msgid = 'help_prereq',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    TextField('target',
        required = False,
        default_content_type = config.DEFAULT_CONTENT_TYPE,
        default_output_type = config.DEFAULT_OUTPUT_TYPE,
        allowable_content_types = config.ALLOWED_CONTENT_TYPES,
        widget = TextAreaWidget(
            label = "Target group",
            description = "Describe for which audience this course is intended",
            label_msgid = 'label_target',
            description_msgid = 'help_target',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    IntegerField('maxParticipants',
        required = False,
        widget = StringWidget(
            label = "Maximum number of participants",
            size = 4,
            description = "If there is an enrollment limit, specify the maximum number of participants",
            label_msgid = 'label_max_participants',
            description_msgid = 'help_max_participants',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    StringField('joinURL',
        required = False,
        widget = StringWidget(
            label = "Registration link",
            description = "Link to the registration for this course. Use 'ecl_register' to let ECLecture handle enrollments for this course.",
            label_msgid = 'label_join_url',
            description_msgid = 'help_join_url',
            size = 65,
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    StringField('directoryEntry',
        required = False,
        widget = StringWidget(
            label = "Directory entry",
            description = "Link to the directory entry for this course.",
            label_msgid = 'label_directory_entry',
            description_msgid = 'help_directory_entry',
            size = 65,
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    StringField('associatedGroup',
        required = False,
        vocabulary = 'getGroupsDisplayList',
        default = NO_GROUP,
        widget = SelectionWidget(
            format = "select", # possible values: flex, select, radio
            label = "Associated group",
            description = """You can associate a group with this course to 
represent its participants; necessary if 'ecl_register' is used for enrollment 
management.""",
            label_msgid = 'label_associated_group',
            description_msgid = 'help_associated_group',
            i18n_domain = config.I18N_DOMAIN,
        ),
    ),

    DataGridField('availableResources',
        searchable = True,
        #default_method = 'getDefaultResources',
        #required = True,
        columns = ('title', 'url'),
        allow_empty_rows = False,
        widget = DataGridWidget(
            label_msgid = 'label_available_resourcess',
            label = "Available resources",
            description_msgid = 'help_available_resources',
            description = """Enter available resources for this course. Title 
is the name of a resource as shown to the user, URL must be a path inside
this site or an URL to an external source. Please remember that published 
items inside this course are added by default.""",
            column_names = ('Title', 'URL',),
            i18n_domain =  config.I18N_DOMAIN,
        ),
    ),

    TextField('text',
        #required=True,
        searchable=True,
        primary=True,
        #storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_content_type = config.DEFAULT_CONTENT_TYPE,
        default_output_type = config.DEFAULT_OUTPUT_TYPE,
        allowable_content_types = config.ALLOWED_CONTENT_TYPES,
        widget = RichWidget(
            label = "Body Text",
            label_msgid = "label_body_text",
            description = "Enter course information",
            description_msgid = "help_body_text",
            rows = 18,
            i18n_domain = config.I18N_DOMAIN,
            allow_file_upload = config.ALLOW_DOCUMENT_UPLOAD,

        )
    ),

),
)


ECLecture_schema = SuperSchema.copy() + schema.copy()

if 'directions' in ECLecture_schema:
    # hide directions field if inheriting from ECFolder
    ECLecture_schema['directions'].widget.visible = {'view' : 'invisible',
                                           'edit' : 'invisible' }
    # move inherited fields to separate edit page
    ECLecture_schema['completedStates'].schemata = 'more'
    ECLecture_schema['projectedAssignments'].schemata = 'more'


class ECLecture(SuperClass):
    """A folder which contains lecture information."""
    security = ClassSecurityInfo()

    implements(interfaces.IECLecture)

    meta_type = 'ECLecture'
    _at_rename_after_creation = True

    schema = ECLecture_schema


    # Methods
    security.declarePublic('isECFolderish')
    def isECFolderish(self):
        """
        @return: True, if ECAssignmentBox is installed and ECLecture is 
                 derived from ECFolder    
        """
        # check whether or not ECAssignmentBox is installed
        qi = getToolByName(self, 'portal_quickinstaller')
        return  qi.isProductInstalled('ECAssignmentBox')

    
    security.declarePublic('getRecurrenceDisplayList')
    def getRecurrenceDisplayList(self):
        """
        Returns a display list of recurrence types.
        """
        dl = DisplayList(())
        
        dl.add(NO_RECURRENCE, _(u'once', default=u'once'))
        dl.add(DAILY, _(u'daily', default=u'daily'))
        dl.add(WEEKLY, _(u'weekly', default=u'weekly'))
        dl.add(MONTHLY, _(u'monthly',default=u'monthly'))
        #dl.add(YEARLY, _(u'yearly', default=u'yearly'))

        return dl

    security.declarePublic('getGroupsDisplayList')
    def getGroupsDisplayList(self):
        """
        Return all available groups as a display list.
        """
        dl = DisplayList(())
        dl.add(NO_GROUP, '----')

        # portal_groups.listGroups is deprecated and will be removed in 
        # Plone 3.5. Use PAS searchGroups instead.
        #pas = getToolByName(self, 'acl_users')
        #groups = pas.searchGroups() 
        
        groups_tool = getToolByName(self, 'portal_groups')
        groups = groups_tool.listGroups()

        #LOG.debug('getGroupsDisplayList: groups: %s' % groups)

        for group in groups:
            dl.add(group.getGroupId(), group.getGroupName())
        
        return dl


    security.declareProtected(permissions.View, 'getLanguagesDL')
    def getLanguagesDL(self):
        """
        Vocabulary method for the courseLanguage field.

        This method is based on languages() in ExtensibleMetadata.py. 
        availableLanguages() is defined in a Script (Python)
        (CMFPlone/skins/plone_scripts/availableLanguages.py)
        """
        available_langs = getattr(self, 'availableLanguages', None)
        if available_langs is None:
            return DisplayList(
                (('en','English'), ('de','German'), ('fr','French'),
                 ('es','Spanish'), ('pt','Portuguese'), ('ru','Russian')))
        if callable(available_langs):
            available_langs = available_langs()
        return DisplayList(available_langs)


    def getGroupMembers(self, groupname):
        """
        This is a horrible workaround for the silly and totally
        unnecessary (the code is already there!) limitation that you
        can't retrieve the group members for groups stored in LDAP.

        Returns a list of member objects.
        
        @deprecated in Plone 3 we shouldn't need this work-around 
        """
        mtool = getToolByName(self, 'portal_membership')
        #gtool = getToolByName(self, 'portal_groups')
        #groups = gtool.listGroupIds()
        
        # listGroupIds will be removed in Plone 3.5
        # we should use searchGroups instead
        #groups = self.acl_users.searchGroups()

        members = []

        if groupname:
            for userid in mtool.listMemberIds():
                if userid:
                    member = mtool.getMemberById(userid)
                    #if 'group_' + groupname in member.getGroups():
                    if str(groupname) in member.getGroups():
                        members.append(member)
            # end for
        # end if

        return members


    def getGroupMembersMailto(self, groupMembers, type=None):
        """
        Return a mailto: link with the e-mail addresses of the users
        given in groupMembers (a list of user names). If type is
        'bcc', create a link that contains the user in the To: header
        and the participants in the Bcc: header.
        """
        currentUser = self.portal_membership.getAuthenticatedMember()
        currentEmail = currentUser.getProperty('email')
        addresses = []

        for user in groupMembers:
            email = user.getProperty('email')
            if email != currentEmail and email not in addresses:
                addresses.append(email)

        if type == 'bcc':
            return 'mailto:?to=%s&bcc=%s' % (currentEmail, ','.join(addresses))
        else:
            return 'mailto:%s' % ','.join(addresses)

        #return 'mailto:' + ','.join([urllib.quote(user.getProperty('email'))
        #                      for user in groupMembers])


    security.declarePublic('isParticipant')
    def isParticipant(self, user_id):
        """
        Returns true, if the associated group contains the given 'user_id'. 
        """
        
        """
        examples from the Web:
        
            member and (member.id in here.portal_groups.getGroupById('group_name').getAllGroupMemberIds())

            membership = getToolByName(self, 'portal_membership')
            if membership.getMemberById(id) is not None:
                return 0
            groups = getToolByName(self, 'portal_groups')
            if groups.getGroupById(id) is not None:
                return 0
        """
        LOG.debug('here we are in ECLecture#isParticipant')

        groups_tool = getToolByName(self, 'portal_groups')
        
        if groups_tool:
            group = groups_tool.getGroupById(str(self.associatedGroup))
        
            if group:
                return (user_id in group.getAllGroupMemberIds())
        #end if
    
        return False


    security.declarePublic('getCurrentParticipants')
    def getCurrentParticipants(self):
        """
        Returns the number of user in the associated group.
        """
        LOG.debug('here we are in ECLecture#getCurrentParticipants')

        groups_tool = getToolByName(self, 'portal_groups')
        
        if groups_tool:
            group = groups_tool.getGroupById(str(self.associatedGroup))
        
            if group:
                return group.getAllGroupMemberIds()
        #end if
        
        return []
        

    security.declarePublic('hasEnrollmentLimitReached')
    def hasEnrollmentLimitReached(self):
        """
        Returns wether or not a user can enroll in this course due to the
        enrollment limit (maxParticipants).
        """
        LOG.debug('here we are in ECLecture#hasEnrollmentLimitReached')

        max = self.getMaxParticipants();
        current = len(self.getCurrentParticipants());
        
        if max: 
            result = not (current < max)
        else:
            result = False
              
        return result
    

    security.declarePublic('addParticipant')
    def addParticipant(self, user_id):
        """
        Add a user to the group associated with this lecture.
        """
        #LOG.info("xdebug: Adding user '%s' to '%s'" % (user_id, self.associatedGroup))

        group = self.acl_users.getGroupByName(str(self.associatedGroup))

        if group:
            try:
                group.addMember(user_id)
            except ValueError, ve:
                # This could happen for users who are not members of the
                # Plone site (e.g., admin)
                LOG.warn('Could not add participant: %s' % ve)
                return False

        else:
            raise Exception('%s is not a valid group.' % str(self.associatedGroup))
            
        return True
            

    security.declarePublic('removeParticipant')
    def removeParticipant(self, user_id):
        """
        Remove a user from the group associated with this lecture.
        """
        LOG.debug('here we are in ECLecture#removeParticipant: %s' % user_id)

        group = self.associatedGroup

        if group:
            try:
                self.acl_users.getGroupByName(group).removeMember(user_id)
            except ValueError, ve:
                # This could happen for users who are not members of the
                # Plone site (e.g., admin)
                LOG.warn('removeParticipant: %s', ve)
                return False
            return True


    security.declarePublic('getTimePeriod')
    def getTimePeriod(self):
        """
        @return a string representing a time period
        """
        value = self.getTimePeriodForEdit()
        return '–'.join(value)


    security.declarePublic('getStartDateWeekday')
    def getStartDateWeekday(self):
        """
        """
        if self.recurrence in [NO_RECURRENCE, WEEKLY]:
            date = self.getField('startDate').get(self)
            if date:
                return date.Day()


    security.declarePrivate('getTimePeriodForEdit')
    def getTimePeriodForEdit(self):
        """
        @return a list with two values representing start and end time of a 
                time period
        """
        value = self.getField('timePeriod').get(self)
        result = []

        try:
            for item in value:
                if type(item) is IntType:
                    result.append('%02d:%02d' % (item/60, item%60))
                elif type(item) is StringType:
                    # When the object is created, this can be the
                    # default value (a string)
                    result.append(item)
        except:
            raise Exception(repr(item))
            
        return result
    
    
#    def getDefaultResources(self):
#        """
#        """
#        slidesTitle = self.translate(domain=I18N_DOMAIN,
#                                     msgid='default_slides_title',
#                                     default='Slides')
#        
#        assignmentsTitle = self.translate(domain=I18N_DOMAIN,
#                                          msgid='default_assignments_title',
#                                          default='Assignments')
#
#        return ({'title':slidesTitle, 'url':'slides', 
#                'icon':'book_icon.gif'},                    
#               {'title':assignmentsTitle, 'url':'assignments', 
#                'icon':'topic_icon.gif'},
#        )

    security.declarePublic('start')
    def start(self):
        """
        Method providing an Event-like interface (works with
        CalendarX, for example).
        """
        date = getattr(self, 'startDate', None)
        return date is None and self.created() or date

    security.declarePublic('end')
    def end(self):
        """
        Method providing an Event-like interface (works with
        CalendarX, for example).
        """
        date = getattr(self, 'endDate', None)
        return date is None and self.start() or date    

    security.declarePublic('lectureTakesPlace')
    def lectureTakesPlace(self, datetime=None):
        """
        Return True if the lecture takes place on the given date. If
        no date is specified, the current date will be used.

        TODO: Currently not implemented for monthly and yearly recurrence.
        """
        
        result = False
        if not datetime:
            datetime = DateTime()

        if datetime >= self.startDate.earliestTime() \
               and datetime <= self.endDate.latestTime():
            if self.recurrence == NO_RECURRENCE:
                result = self.startDate.isCurrentDay()
            elif self.recurrence == DAILY:
                result = True
            elif self.recurrence == WEEKLY:
                result = datetime.dow() == self.startDate.dow()
            elif self.recurrence == MONTHLY:
                # TODO
                result = False
            elif self.recurrence == YEARLY:
                # TODO
                result = False
        return result


registerType(ECLecture, config.PROJECTNAME)
# end of class ECLecture
