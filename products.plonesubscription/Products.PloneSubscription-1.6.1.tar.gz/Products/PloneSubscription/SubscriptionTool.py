# -*- coding: utf-8 -*-
## PloneSubscription
## A Plone tool supporting different levels of subscription and notification
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module implements generic functions for subscriptions
"""
__version__ = "$Revision: 61009 $"
# $Source$
# $Id: SubscriptionTool.py 241667 2011-06-29 22:19:01Z yboussard $
__docformat__ = 'restructuredtext'

# Python imports
import socket
import md5
from smtplib import SMTPException

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from AccessControl.SecurityManagement import noSecurityManager
from DateTime import DateTime
from Products.MailHost.MailHost import MailHostError
from zLOG import LOG, INFO

# CMF imports
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFPlone.PropertiesTool import SimpleItemWithProperties
from Products.statusmessages.interfaces import IStatusMessage

# Archetypes imports
from Products.Archetypes.public import *
from Products.Archetypes.Renderer import renderer

# Products imports
from Products.PloneSubscription.config import *
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscription import ISubscription
from Products.PloneSubscription.interfaces.ISubscriber import ISubscriber
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

# import from schema
from Products.PloneSubscription.content.schemata import FormAddGroupSubscriptionSchema
import logging
logger = logging.getLogger('Products.SubscriptionTool')

_MARKER = 'Marker'

# Subscription tool schema. Only reference field will be editable
schema = BaseFolderSchema.copy() + Schema((
    BooleanField(
        'authorize_root_subscription',
        searchable=False,
        default=False,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Authorize root subscription",
            label_msgid="label_subscription_authorize_root_subscription",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'anonymous_unsubscribe_by_email',
        searchable=False,
        default=False,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Anonymous unsubscription by email?",
            label_msgid="label_anonymous_unsubscribe_by_email",
            description="Should anonymous subscribers receive an email with unsubscription information instead of directly unsubscribing by giving their email address?",
            description_msgid="help_anonymous_unsubscribe_by_email",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'show_actions',
        searchable=False,
        default=False,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Show actions",
            label_msgid="label_subscription_show_actions",
            description="Show actions permitting to add providers in the site.",
            description_msgid="help_subscription_show_actions",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'hide_remove_button',
        searchable=False,
        default=True,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Hide remove button",
            label_msgid="label_subscription_hide_remove_button",
            description="Hides remove button in 'my subscriptions' if nothing is selected.",
            description_msgid="help_subscription_hide_remove_button",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'show_document_action',
        searchable=False,
        default=True,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            label="Show subscription document action",
            label_msgid="label_subscription_show_document_action",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'show_subscription_portlet',
        searchable=False,
        default=True,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            label="Show subscription portlet",
            label_msgid="label_subscription_show_subscription_portlet",
            i18n_domain="plonesubscription",
            ),
        ),
    BooleanField(
        'show_keywords_portlet',
        searchable=False,
        default=True,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=BooleanWidget(
            label="Show keywords search portlet",
            label_msgid="label_subscription_show_keywords_portlet",
            i18n_domain="plonesubscription",
            ),
        ),
    ReferenceField(
        'provider',
        multiValued=False,
        required=True,
        searchable=False,
        relationship='subscriptionProviderOf',
        allowed_types=('SubscriptionProvider',),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=ReferenceBrowserWidget(
            destination_types=['SubscriptionProvider',],
            addable=False,
            allow_search=0,
            allow_browse=1,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Subscription container provider",
            label_msgid="label_subscription_provider",
            description="Folder which provide base subscription functionnality.",
            description_msgid="help_subscription_provider",
            i18n_domain="plonesubscription",
            ),
        ),
    ReferenceField(
        'templates',
        multiValued=False,
        required=True,
        searchable=False,
        relationship='templatesProviderOf',
        allowed_types=('TemplatesProvider',),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=ReferenceBrowserWidget(
            destination_types=['TemplatesProvider',],
            addable=False,
            allow_search=0,
            allow_browse=1,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Templates provider",
            label_msgid="label_subscription_templates",
            description="Folder which provide base templates.",
            description_msgid="help_subscription_templates",
            i18n_domain="plonesubscription",
            ),
        ),
    IntegerField(
        'periodicity',
        required=True,
        searchable=True,
        default=60,
        vocabulary='getPeriodicityVocabulary',
        enforceVocabulary=True,
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=SelectionWidget(
            label="Mail periodicity",
            label_msgid="label_subscription_periodicity",
            description="Periodicity used to send subscriptions mails.",
            description_msgid="help_subscription_periodicity",
            i18n_domain="plonesubscription",
            ),
        ),
    LinesField(
        'base_url',
        required=False,
        searchable=False,
        default=('http://127.0.0.1:8080/plone', 'http://www.example.org'),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=LinesWidget(
            label="Base url",
            label_msgid="label_subscription_base_url",
            description="Site base url.",
            description_msgid="help_subscription_base_url",
            i18n_domain="plonesubscription",
            # specific
            rows=4,
            cols=42,
            ),
        ),
    ReferenceField(
        'folderTemplate',
        multiValued=False,
        required=False,
        searchable=False,
        relationship='folderTemplateOf',
        allowed_types=('SubscriptionTemplate',),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=ReferenceBrowserWidget(
            destination_types=['SubscriptionTemplate',],
            addable=False,
            allow_search=0,
            allow_browse=1,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Folder subscription template",
            label_msgid="label_subscription_folder_template",
            description="Template for folder subscription.",
            description_msgid="help_subscription_folder_template",
            i18n_domain="plonesubscription",
            ),
        ),
    ReferenceField(
        'contentTemplate',
        multiValued=False,
        required=False,
        searchable=False,
        relationship='contentTemplateOf',
        allowed_types=('SubscriptionTemplate',),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=ReferenceBrowserWidget(
            destination_types=['SubscriptionTemplate',],
            addable=False,
            allow_search=0,
            allow_browse=1,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Content subscription template",
            label_msgid="label_subscription_content_template",
            description="Template for folder subscription.",
            description_msgid="help_subscription_content_template",
            i18n_domain="plonesubscription",
            ),
        ),
    ReferenceField(
        'keywordsTemplate',
        multiValued=False,
        required=False,
        searchable=False,
        relationship='keywordsTemplateOf',
        allowed_types=('SubscriptionTemplate',),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=ReferenceBrowserWidget(
            destination_types=['SubscriptionTemplate',],
            addable=False,
            allow_search=0,
            allow_browse=1,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Keywords subscription template",
            label_msgid="label_subscription_keywords_template",
            description="Template for keywords subscription.",
            description_msgid="help_subscription_keywords_template",
            i18n_domain="plonesubscription",
            ),
        ),
    ReferenceField(
        'exactSearchTemplate',
        multiValued=False,
        required=False,
        searchable=False,
        relationship='exactSearchTemplateOf',
        allowed_types=('SubscriptionTemplate',),
        read_permission=CMFCorePermissions.View,
        write_permission=SubscriptionPermissions.ManageSubscriptionContent,
        widget=ReferenceBrowserWidget(
            destination_types=['SubscriptionTemplate',],
            addable=False,
            allow_search=0,
            allow_browse=1,
            startup_directory='/',
            force_close_on_insert=1,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Exact Search subscription template",
            label_msgid="label_subscription_exactsearch_template",
            description="Template for exact search subscription.",
            description_msgid="help_subscription_exactsearch_template",
            i18n_domain="plonesubscription",
            ),
        ),
    ),)
schema['id'].widget.visible = { 'view': 'visible', 'edit': 'hidden',}
schema['title'].widget.visible = { 'view': 'visible', 'edit': 'hidden',}
schema['description'].widget.visible = { 'view': 'visible', 'edit': 'hidden',}


class SubscriptionTool(UniqueObject, BaseFolder):
    """A tool to manage placeless subscription"""

    plone_tool = 1
    id = 'portal_subscription'
    title = "Placeless Subscription tool for Plone"
    portal_type = meta_type = TOOL_META_TYPE
    manage_options = BaseFolder.manage_options

    # AT specific
    archetype_name = "Subscription Tool"
    immediate_view = 'base_view'
    default_view   = 'base_view'
    global_allow = False
    allowed_content_types = ()
    schema = schema
    include_default_actions = 1

    # Tool specific
    security = ClassSecurityInfo()

    actions = (
        {
        'id'            : 'view',
        'name'          : 'View',
        'action'        : 'string:${object_url}/base_view',
        'condition'     : '',
        'permissions'   : (SubscriptionPermissions.ManageSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
        {
        'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'string:${object_url}/base_edit',
        'condition'     : '',
        'permissions'   : (SubscriptionPermissions.ManageSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
        {
        'id'            : 'subscribers_management',
        'name'          : 'Manage Subscribers',
        'action'        : 'string:${object_url}/subscribers_management',
        'condition'     : '',
        'permissions'   : (SubscriptionPermissions.ManageSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
    )

    # initialization

    def __init__(self):
        BaseFolder.__init__(self, self.id)

    # accessor and mutator overload

    security.declarePublic('showActions')
    def showActions(self):
        """give public accessor for show_actions"""
        return self.getShow_actions()

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'setPeriodicity')
    def setPeriodicity(self, periodicity, **kw):
        """Synchronise field data with subscription_task"""
        self.getField('periodicity').set(self, periodicity)

        mtool = getToolByName(self, 'portal_maintenance', None)
        if not mtool:
            return
        subscription_task = getattr(mtool.tasks, subscription_task_id, None)
        if not subscription_task:
            return

        if periodicity == '60':
            subscription_task.scheduled_month = '*'
            subscription_task.scheduled_day_of_month = '*'
            #subscription_task.scheduled_day_of_week = '*'
            subscription_task.scheduled_hour = '*'
            subscription_task.scheduled_minute = '1'
        elif periodicity == '1440':
            subscription_task.scheduled_month = '*'
            subscription_task.scheduled_day_of_month = '*'
            #subscription_task.scheduled_day_of_week = '*'
            subscription_task.scheduled_hour = '1'
            subscription_task.scheduled_minute = '1'
        elif periodicity == '10080':
            subscription_task.scheduled_month = '*'
            subscription_task.scheduled_day_of_month = '*'
            #subscription_task.scheduled_day_of_week = '*'
            subscription_task.scheduled_hour = '1'
            subscription_task.scheduled_minute = '1'
        elif periodicity == '43200':
            subscription_task.scheduled_month = '*'
            subscription_task.scheduled_day_of_month = '1'
            #subscription_task.scheduled_day_of_week = '1'
            subscription_task.scheduled_hour = '1'
            subscription_task.scheduled_minute = '1'
        elif periodicity == '525600':
            subscription_task.scheduled_month = '1'
            subscription_task.scheduled_day_of_month = '1'
            #subscription_task.scheduled_day_of_week = '1'
            subscription_task.scheduled_hour = '1'
            subscription_task.scheduled_minute = '0'

    security.declareProtected(CMFCorePermissions.View, 'getBaseUrl')
    def getBaseUrl(self, **kwargs):
        """Wrapper to get wanted base_url value

        Done to be monkey patched for multi virtualhost sites.
        """
        return self.getField('base_url').get(self)[0]

    # methods
    security.declarePublic('hasSubscription')
    def hasSubscription(self, memberid=None):
        """Return True if the user has at least one subscription
           Used to decide whether the "my subscriptions" action is
           to be shown or not.
           Only works for anonymous currently, but could work with cookies.
        """
        has_subscriptions = False
        if not memberid:
            mtool = getToolByName(self, 'portal_membership')
            if not mtool.isAnonymousUser():
                member = mtool.getAuthenticatedMember()
                memberid = member.getId()
        has_subscriptions = self.getSubscriptions(subscriber_id=memberid, flag_only=1)
        return has_subscriptions

    security.declarePublic('getSubscriberId')
    def getSubscriberId(self):
        subscriber_id = None
        mtool = getToolByName(self, 'portal_membership')
        if not mtool.isAnonymousUser():
            member = mtool.getAuthenticatedMember()
            subscriber_id = member.getId()
        return subscriber_id

    security.declarePublic('getSubscriber')
    def getSubscriber(self, subscriber_id=''):
        """Return subscriber where subscriptions are stored by default
           For Members, this will be a folder called like the member id
           For Anonymous, we can not return a subscriber.
        """
        # if no id is given, we assume that's the authenticated member's id
        subscriber=None
        if not subscriber_id:
            subscriber_id=self.getSubscriberId()
        if subscriber_id:
            provider = self.getProvider()
            subscriber = getattr(provider, subscriber_id, None)
        return subscriber

    security.declarePublic('isSubscribedTo')
    def isSubscribedTo(self, content, subscriber_id):
        """Checks whether the user has a subscription to the content"""
        is_subscribed_to = False
        subscriptions = self.getSubscriptions(content, subscriber_id)
        if len(subscriptions)>0:
            is_subscribed_to=True
        return is_subscribed_to

    security.declarePublic('getAnonymousSubscriberId')
    def getAnonymousSubscriberId(self, key):
        """
        Remove a subscription to the content.
        """
        return md5.md5(key).hexdigest()

    security.declarePublic('removeSubscription')
    def removeSubscription(self, content, subscriber_id=None):
        """
        Remove a subscription to the content.
        """
        is_anonymous=0
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            is_anonymous=1
        if subscriber_id:
           pass
        else:
            # Differentiate between anonymous and member subscribers for access
            if is_anonymous:
                email = self.REQUEST.get('email')
                subscriber_id = self.getAnonymousSubscriberId(email)
            else:
                member = mtool.getAuthenticatedMember()
                subscriber_id = member.getId()

        stool = getToolByName(self, 'portal_subscription')
        if is_anonymous:
            def getRolesInContext(self, context):
                return ['Manager',]
            def getRoles(self):
                return ['Manager',]
            OmnipotentUser.getRolesInContext = getRolesInContext
            OmnipotentUser.getRoles = getRoles
            portal = getToolByName(self, 'portal_url').getPortalObject()
            newSecurityManager(None, OmnipotentUser().__of__(portal.acl_users))

        subscriber = self.getSubscriber(subscriber_id)
        subscriptions = stool.getSubscriptions(content, subscriber_id)
        ids = []
        parent = None
        for subscription in subscriptions:
            subscription_object=subscription.getObject()
            if subscription_object:
                ids.append(subscription_object.getId())
                if not parent:
                    parent = subscription_object.getParentNode()
        if ids:
            parent.manage_delObjects(ids=ids)
            message = 'psm_content_removed_from_my_subscriptions'
        else:
            message = "No subscription found."

        if is_anonymous:
            message = 'psm_content_removed_from_my_subscriptions'
            noSecurityManager()

        return message

    security.declarePublic('setSubscription')
    def setSubscription(self, id='', ptype='', subscriber_uid='', **kw):
        """Create or modify a subscription for a user

        If you have a existing ptype implementing ISubscription we try to catch
        or create the object then we modify it with keywords argument.

        Keywords have to contain rpath and title key.
        """
        # Do not create anything if the portal type doesn't exist
        types_tool = getToolByName(self, 'portal_types')
        uid_catalog = getToolByName(self, 'uid_catalog')
        if ptype not in types_tool.objectIds():
            return None

        # Differentiate between anonymous and member subscribers for access
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            subscriber_id = self.getAnonymousSubscriberId(kw['email'])
            subscriber_type = 'AnonymousSubscriber'
        else:
            member = mtool.getAuthenticatedMember()
            subscriber_id = member.getId()
            subscriber_type = 'UserSubscriber'

        # If UID is given, search in UID catalog or get the subscriber by id
        if subscriber_uid:
            subscriber = uid_catalog(UID=subscriber_uid)[0].getObject()
        else:
            subscriber = self.getSubscriber(subscriber_id)

        # Subscriber is not known, so add it, and get it
        if subscriber is None:
            provider = self.getProvider()
            provider.invokeFactory(subscriber_type, subscriber_id)
            subscriber = self.getSubscriber(subscriber_id)

        portal_url = getToolByName(self, 'portal_url')
        rpath = kw.get('rpath', '')
        # transform the rpath to be getPhysicalPath compatible
        if ptype not in ('ContentSubscription', 'FolderSubscription') and \
           rpath and rpath[0] == '/':
            kw['rpath'] = "%s%s" % ('/'.join(portal_url.getPhysicalPath()[:-1]), rpath)
        else:
            kw['rpath'] = "%s/%s" % ('/'.join(portal_url.getPhysicalPath()[:-1]), rpath)

        subscription = None
        if id == '':
            id = subscriber.generateUniqueId(ptype)
            subscription = None
        else:
            subscription = getattr(subscriber, id, None)

        if subscription:
            message = 'psm_subscriptions_updated'
        else:
            # Archetypes can set kwargs on creation, we edit() it after
            LOG("PloneSubscription.SubscriptionTool.setSubscription call debug: id", INFO,
                repr(id))
            LOG("PloneSubscription.SubscriptionTool.setSubscription call debug: ptype", INFO,
                repr(ptype))
            LOG("PloneSubscription.SubscriptionTool.setSubscription call debug: subscriber_uid", INFO,
                repr(subscriber_uid))
            LOG("PloneSubscription.SubscriptionTool.setSubscription call debug: kwargs", INFO,
                repr(kw))
            subscriber.invokeFactory(ptype, id)
            subscription = getattr(subscriber, id)

            # We don't want results earlier than the subscription creation
            kw['last_send'] = subscription.created()

            if subscription:
                if ISubscription.isImplementedBy(subscription):
                    subscription.edit(**kw)
                else:
                    raise "Subscription interface not supported!"

                message = 'psm_subscriptions_page_added'
            else:
                message = 'psm_subscriptions_page_not_added'

        return message

    security.declarePublic('getAnonymousSubscription')
    def getAnonymousSubscription(self, content, subscriber_id):
        if content.meta_type=="Plone Site":
            # In case we are on the root folder, we have to take subscriptions from
            # the portal_subscription tool. Let's hope the Portal site will be
            # an Archetype soon
            brefs = self.getBRefs(relationship='subscriptionContentOf')
        else:
            brefs = content.getBRefs(relationship='subscriptionContentOf')
        for subscription in brefs:
            if subscription.getSubscriber().getId()==subscriber_id:
                return subscription

    # _robert intoduced flag_only so the subscriptions do not wake up objects
    # this could result in returning subsciptions when there are only bad pointers
    # which is less bad than waking objects on each call
    security.declarePublic('getSubscriptions')
    def getSubscriptions(self, content=None, subscriber_id='', flag_only=0):
        """Return Subscription stored in a SubscriptionFolder list in a dict
           Attention: This depends on the permissions of the user, as it is
                      using the catalog!
        """
        catalog = self.getCatalog()
        search_dict = {}
        Log(LOG_DEBUG, 'getSubscriptions parameters', content, subscriber_id)
        if content:
            search_dict['rpath'] = '/'.join(content.getPhysicalPath())
        if subscriber_id:
            provider = self.getProvider()
            if provider:
                search_dict['path'] = '%s/%s' % ('/'.join(provider.getPhysicalPath()), subscriber_id)
        Log(LOG_DEBUG, 'getSubscriptions search dict', search_dict)
        if content:
            subscriptions = []
            for result in catalog.searchResults(search_dict):
                result_object = result.getObject()
                Log(LOG_DEBUG, 'getSubscription subscriptions', result_object)
                if result_object:
                    if result_object.getRefs(relationship='subscriptionContentOf'):
                        if result_object.getRefs(relationship='subscriptionContentOf')[0]==content:
                            subscriptions.append(result)
                    if result_object.getRefs(relationship='subscriptionFolderOf'):
                        if result_object.getRefs(relationship='subscriptionFolderOf')[0]==content:
                            subscriptions.append(result)
        else:
            subscriptions = []
            for result in catalog.searchResults(search_dict):
                #  _robert if we want only a flag whether user has any subscription
                # we return True or False
                if flag_only:
                    return True
                result_object = result.getObject()
                if result_object:
                    subscriptions.append(result)
        #_robert
        if flag_only:
            return False
        return subscriptions

    security.declarePublic('countSubscriptions')
    def countSubscriptions(self, content):
        """Return the subscription count
        """
        count = 0
        if content.meta_type == "Plone Site":
            # In case we are on the root folder, we have to take subscriptions from
            # the portal_subscription tool. Let's hope the Portal site will be
            # an Archetype soon
            brefs = self.getBRefs(relationship='subscriptionContentOf')
        else:
            brefs = content.getBRefs(relationship='subscriptionContentOf')
        if brefs:
            count=len(brefs)
        else:
            count=0
        return count

    security.declarePublic('getCatalog')
    def getCatalog(self):
        """Return subscription provider catalog"""
        catalog = None
        portal = getToolByName(self, 'portal_url').getPortalObject()
        catalog = getattr(portal,'subscription_catalog', None)
        return catalog

    security.declarePublic('getPeriodictyVocabulary')
    def getPeriodicityVocabulary(self):
        """Return strict periodicity vocabulary

        Use minutes for key to help DateTime operations
        """
        return Vocabulary(DisplayList((
            ('1', "Minutely", 'periodicity_minutely'),
            ('60', "Hourly", 'periodicity_hourly'),
            ('1440', "Daily", 'periodicity_daily'),
            # Not implemented in PloneMaintenance for the moment
            #('10080', "Weekly", 'periodicity_weekly'),
            ('43200', "Monthly", 'periodicity_monthly'),
            ('525600', "Yearly", 'periodicity_yearly'),
            )), self, 'plonesubscription')

    security.declarePublic('getGroupSubscriberVocabulary')
    def getGroupSubscriberVocabulary(self):
        """ Return a Vocabulary of created GroupSubscriber for adding group
            subscription interface
        """
        stool = getToolByName(self, 'portal_subscription')
        provider = stool.getProvider()
        uids_and_titles=[]
        for subscriber in provider.objectValues():
            if subscriber.meta_type=="GroupSubscriber":
                uids_and_titles.append( (subscriber.UID(), subscriber.title_or_id() ) )
        return Vocabulary(DisplayList(uids_and_titles), self, 'plonesubscription')

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getSubscriptionTemplate')
    def getSubscriptionTemplate(self, subscription=None):
        """get the template to use with a subscription"""
        ptype = subscription.portal_type

        if ptype == 'FolderSubscription' and self.getFolderTemplate() is not None:
            template = self.getFolderTemplate().getMail_body()
        elif ptype == 'ContentSubscription' and self.getContentTemplate() is not None:
            template = self.getContentTemplate().getMail_body()
        elif ptype == 'KeywordsSubscription' and self.getKeywordsTemplate() is not None:
            template = self.getKeywordsTemplate().getMail_body()
        elif ptype == 'ExactSearchSubscription' and self.getExactSearchTemplate() is not None:
            template = self.getExactSearchTemplate().getMail_body()
        else:
            template = """
A change related to your subscription to "%(subscription_title)s" was found:

%(content)s
"""
        return template

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'updateDateForAllSubscriptions')
    def updateDateForAllSubscriptions(self):
        """ usefull when you don't want send mail ,
        this method update subscription for all user """
        now = DateTime()
        subscriptions = self.getUpdatedSubscriptions(now)
        for subscription in self.getUpdatedSubscriptions(now):
            subscription.setLast_send(now)
        try:
            IStatusMessage(self.REQUEST).addStatusMessage('Updated %d subscriptions' % len(subscriptions),
                                                          type="info")
            return self.subscribers_management()
        except:
            pass


    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getUpdatedSubscriptions')
    def getUpdatedSubscriptions(self, date):
        """Get all updated subscription since a date.
           Returns the subscription objects."""
        subscriptions =[]
        periodicity = self.getPeriodicity()
        query = {'getLast_Send':{'query': [date - float(periodicity) / 1440.0,],
                                 'range': 'max',
                                },
                }
        catalog = self.getCatalog()
        for subscription in catalog.searchResults(query):
            subscriptions.append(subscription.getObject())
        return subscriptions

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'simulateMailing')
    def simulateMailing(self):
        """ usefull when you don't want send mail ,
        and you want to see what do the subcriber tool"""

        r = self.mailing(preview=1)
        try:
            if r:
                for (i,mail) in enumerate(r):
                    IStatusMessage(self.REQUEST).addStatusMessage("%d : %s" %
                                                                  (i,unicode(mail,'utf8','ignore')),
                                                                  type="info")
            else:
                
                IStatusMessage(self.REQUEST).addStatusMessage('No mail to be send',
                                                              type="info")
            return self.subscribers_management()
        except:
            logger.exception('there is an error')
            pass

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'doMailing')
    def doMailing(self):
        """ fire the subcriber tool"""

        self.mailing()
        try:
            IStatusMessage(self.REQUEST).addStatusMessage("Mailling done")
           
            return self.subscribers_management()
        except:
            logger.exception('there is an error')
            pass


    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'mailing')
    def mailing(self, preview=0):
        """Searches for all subscriptions that haven't been sent according to
           the peridiocity setting in the subscription tool by comparing with
           the last sent date on the subscriptions.

           Each subscription has users associated, so for each user, the
           subscription content is searched. All subscription content for one
           subscription and one user is assembled sent per user and
           subscription.

           If preview is set, the mails that would have been sent are returned
           as a list of mail texts.
        """
        if preview:
            mails = []
        now = DateTime()
        current_user = getSecurityManager().getUser()
        for subscription in self.getUpdatedSubscriptions(now):
            Log(LOG_DEBUG, 'subscription', subscription.id)
            is_one_mail_sent = False
            subscriber = subscription.getSubscriber()

            for user in subscriber.getUsers(subscription.getId()):
                Log(LOG_DEBUG, 'user', user)
                if self.validate_mailing_by_user(now, subscription, user):
                    # Search as subscribed user
                    newSecurityManager(None, user)
                    unfiltered_brains = subscription.getQueryBrains()
                    brains = subscription.afterQueryFilters(unfiltered_brains)
                    # Restore current user
                    newSecurityManager(None, current_user)
                    Log(LOG_DEBUG, 'brains for a valid user all/filtered:', unfiltered_brains, brains)
                    # /!\ Be careful: brains are LazyMap but not list or tuple.
                    if brains:
                        mail = self.mailing_by_user(now, subscription, user, brains)
                        Log(LOG_DEBUG, 'mail sent', mail)
                        if preview:
                            mails.append(mail)
                        else:
                            if self.sendMail(mail):
                                is_one_mail_sent = True

            Log(LOG_DEBUG, 'update last send date: ', is_one_mail_sent)
            if is_one_mail_sent:
                subscription.setLast_send(now)
            
        if preview:
            return mails
        else:
            Log(LOG_DEBUG, "Mailing done")
            return 'mailing done'

    security.declarePrivate("validate_mailing_by_user")
    def validate_mailing_by_user(self, now, subscription, user):
        """ Validate that the mail by user can and should be done.
        """
        validation=True

        if user is None:
            return False

        last_send = subscription.getLast_send()

        if last_send == subscription.created():
            # If the subscription was just added (the last send date equals
            # the creation date), the periodicity is not taken into account
            # at all.
            pass
        else:
            # After the first sending, the periodicity is making sure that
            # nothing is sent again that was sent before.
            periodicity = float(self.getPeriodicity()) / 1440.0
            # Be careful, last_send can be 'None'
            if last_send and now - last_send < periodicity:
                validation = False

        if user.getId() == "Anonymous User":
            # Check if anonymous has an email
            if user.getProperty('email') in (None, ''):
                validation = False
        elif user.getId() is not None:
            # Verification of member
            mtool = getToolByName(self, 'portal_membership')
            member = mtool.getMemberById(user.getId())

            # Check if member exists
            if member is None:
                validation = False # perhaps a user from Zope root acl_users?

            # Check if member has an email
            if member and member.getProperty('email') in (None, ''):
                validation = False
        else:
            validation = False

        return validation

    security.declarePrivate("mailing_by_user")
    def mailing_by_user(self, now, subscription, user, brains):
        """ Mail users about all content changes pertaining to a subscription
        """
        info = self.mailing_by_user_info(now, user, subscription)
        mail = self.getHeaders(info)
        mail += "\n\n"
        mail += self.mailing_by_user_body(subscription, brains)
        return mail

    security.declarePrivate("mailing_by_user_headers")
    def mailing_by_user_info(self, now, user, subscription):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        ptool = getToolByName(self, 'portal_properties')
        mail_from = portal.getProperty('email_from_address',
                                       'admin@plone-subscription.com')
        mtool = getToolByName(self, 'portal_membership')

        if user.getId()=="Anonymous User":
            mail_to = user.getProperty('email')
        else:
            member = mtool.getMemberById(user.getId())
            mail_to = member.getProperty('email')

        charset = ptool.site_properties.getProperty('default_charset', 'utf-8')
        headers_infos = {'date': now.rfc822(),
                         'mail_from': mail_from,
                         'mail_to': mail_to,
                         'subject': subscription.Title(),
                         'charset': charset,
                        }
        return headers_infos

    security.declarePrivate("mailing_by_user_body")
    def mailing_by_user_body(self, subscription, brains):
        """Render the mail body for the subscription and the brains.
        """
        portal_path = getToolByName(self, 'portal_url').getPortalPath()
        portal_path_length = len(portal_path)
        base_url = self.getBaseUrl()
        content = ''
        Log(LOG_DEBUG, 'subscription brains', brains)
        for brain in brains:
            content += "    "
            content += str(brain.Title or brain.getId)
            content += " :\n"
            obj = brain.getObject()
            if base_url == '':
                content += str(obj.absolute_url())
            else:
                content += base_url
                content += str(obj.absolute_url_path()[portal_path_length:])
            content += "\n\n"
        Log(LOG_DEBUG, 'subscription content', content)
        template = self.getSubscriptionTemplate(subscription)
        body =  template % {'subscription_title': subscription.TitleOrId(),
                            'content': content,
                           }
        return body

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'mailing')
    def contactMailing(self, content, emails, from_email, subject, message):
        """Contact all subscribers concering some content"""
        ptool = getToolByName(self, 'portal_properties')
        charset = ptool.site_properties.getProperty('default_charset', 'utf-8')
        headers_infos = {
            'date': DateTime().rfc822(),
            'mail_from': from_email,
            'mail_to': '',
            'subject': subject,
            'charset': charset,
            }
        template = self.getContactTemplate()
        content_info = ''
        content_info += "    " + str(content.title_or_id()) + " :\n"
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_path = getToolByName(self, 'portal_url').getPortalPath()
        portal_path_length = len(portal_path)
        base_url = self.getBaseUrl()
        if base_url == '':
            content_info += str(content.absolute_url()) + "\n\n"
        else:
            content_info += base_url + str(content.absolute_url_path()[portal_path_length:]) + "\n\n"
        content_info += message + "\n\n"
        body =  template % {'subscription_title': content.title_or_id(),
                            'content': content_info,
                           }
        successes = 0
        for email in emails:
            headers_infos['mail_to'] = email
            if self.sendMail(self.getHeaders(headers_infos) + "\n\n" + body):
                successes += 1
        if successes == 0:
            message = "None of the %s messages were sent." % len(emails)
        elif successes < len(emails):
            message = "Only %s of %s mails sent successfully." % (successes, len(emails))
        else:
            message = "All %d messages sent successfully" % len(emails)
        Log(LOG_DEBUG, "Contact Mailing done")
        return message

    security.declarePublic('unsubscriptionMailing')
    def unsubscriptionMailing(self, content, email):
        """Contact all subscribers concering some content"""
        portal = getToolByName(self, 'portal_url').getPortalObject()
        ptool = getToolByName(self, 'portal_properties')
        charset = ptool.site_properties.getProperty('default_charset', 'utf-8')
        from_email = portal.getProperty('email_from_address', 'admin@plone-subscription.com')
        headers_infos = {
            'date': DateTime().rfc822(),
            'mail_from': from_email,
            'mail_to': '',
            'subject': 'Unsubscription from ' + str(content.title_or_id()),
            'charset': charset,
            }
        template = self.getUnsubscriptionTemplate()
        content_info = ''
        content_info += "    " + str(content.title_or_id()) + " :\n"
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_path = getToolByName(self, 'portal_url').getPortalPath()
        portal_path_length = len(portal_path)
        base_url = self.getBaseUrl()
        if base_url == '':
            content_info += str(content.absolute_url()) + "\n\n"
        else:
            content_info += base_url + str(content.absolute_url_path()[portal_path_length:]) + "\n\n"

        subscriber_id = self.getAnonymousSubscriberId(email)
        subscription = self.getAnonymousSubscription(content, subscriber_id)
        if subscription:
            removal_id=subscription.getId()
            Log(LOG_DEBUG, "SubscriptionTool.unsubscriptionMailing removal_id: %s\n\n" % removal_id)
            content_info += "To unscubscribe, click the folling link:" + "\n\n"
            content_info += content.absolute_url() + '/removeSubscription?id='+ subscriber_id + "\n\n"
            body = template % {'subscription_title': content.title_or_id(),
                                'content': content_info,
                               }
            successes = 0
            headers_infos['mail_to'] = subscription.getSubscriber().getSubscriberInfo()['email']
            if self.sendMail(self.getHeaders(headers_infos) + "\n\n" + body):
                successes += 1
                Log(LOG_DEBUG, "Message sent to " + headers_infos['mail_to'])
            if successes == 0:
                Log(LOG_DEBUG, "No message sent for content " + content.absolute_url() + ", subscriber_id :" + str(subscriber_id))
                #message = "An error occurred while trying to send unsubscription information."
                # Keep lying to dissimulate the fact that failed to send a mail as we know there is a subscription.
                message = "Email with unsubscription information sent."
            else:
                message = "Email with unsubscription information sent."
        else:
            # Keep lying to dissimulate the fact that we have no subscription for this email.
            message = "Email with unsubscription information sent."
            Log(LOG_DEBUG, "No message sent for content " + content.absolute_url() + ", subscriber_id :" + str(subscriber_id))
        return message

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getSubscriptionTemplate')
    def getContactTemplate(self):
        """get the template to use with contacting all subscribers"""
        template = """A message concerning your subscription to "%(subscription_title)s":

%(content)s
"""
        return template

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getUnsubscriptionTemplate')
    def getUnsubscriptionTemplate(self):
        """get the template to use with unsubscription"""
        template = """A message concerning your unsubscription from "%(subscription_title)s":

%(content)s
"""
        return template

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'getHeaders')
    def getHeaders(self, headers_infos={}):
        """ return mail headers

        take a dictionnary with five item:
        - date
        - mail_from
        - mail_to
        - subject
        - charset
        """

        headers = """Date: %(date)s
From: %(mail_from)s
To: %(mail_to)s
Subject: %(subject)s
Content-Type: text/plain; charset=%(charset)s
"""
        return headers % headers_infos

    security.declarePrivate('sendMail')
    def sendMail(self, messageText, mto=None, mfrom=None, subject=None, encode=None):
        """Send a preformatted mail"""
        mail_sent=True
        
        if TRACE_SEND_MAIL:
            logger.info('SubscriptionTool.sendMail '
                        'message:\n %s ' % (messageText))
        else:
            Log(LOG_DEBUG, "SubscriptionTool.sendMail : mail body\n\n %s" % messageText)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        try:
            portal.MailHost.send(messageText, mto, mfrom, subject, encode)
        except (socket.error, MailHostError, SMTPException, AttributeError), error_msg:
            Log(LOG_NOTICE, "SubscriptionTool.sendMail",
                "Error while sending mail:\n %s" % error_msg)
            mail_sent=False
        return mail_sent

    # rendering utils

    security.declarePublic('renderEmptyWidget')
    def renderEmptyWidget(self, instance, field, mode, **kwargs):
        """Render empty widget from field"""

        accessor = field.getAccessor(instance)
        widget = field.widget
        field_name = field.getName()
        return renderer.render(field_name=field_name, mode=mode, widget=widget,
                               instance=instance, field=field, accessor=accessor,
                               **kwargs)

    security.declarePublic('getFormAddGroupedSubscriptionFields')
    def getFormAddGroupedSubscriptionFields(self):
        """ Return adding grouped subscription form schema fields """
        return FormAddGroupSubscriptionSchema.fields()

    security.declarePrivate('getQueryBrains')
    def getQueryBrains(self, query):
        """Return the list of brains concerned by the mailing using the query"""
        brains = []
        ctool = getToolByName(self, 'portal_catalog')
        brains = ctool.searchResults(**query)
        return brains

    security.declarePrivate('afterQueryWorkflowFilter')
    def afterQueryWorkflowFilter(self, brains, last_send, transitions=[]):
        """Filter the list of brains for a workflow change depending on the
           last send time.
        """
        results = []
        wtool = getToolByName(self, 'portal_workflow')
        for brain in brains:
            history = wtool.getInfoFor(brain.getObject(), 'review_history', [])
            for trans in history:
               if trans.has_key('time') and trans['time'] > last_send:
                   if transitions:
                       if trans.has_key('action') and trans['action'] in transitions:
                           results.append(brain)
                           break
                   else:
                       results.append(brain)
                       break
        return results

registerType(SubscriptionTool, PROJECTNAME)

# These methods would be useful with Zope 2.8 to get types implementing some
# services interfaces.

def getInterfaceImplementedBy(interface):
    """Return a list of portal_types implementing an interface"""
    return tuple([type['name'] for type in listTypes()
                  if interface.isImplementedByInstancesOf(type['klass'])])

def getSubscriberAllowedContentTypes():
    """Return portal_types implementing ISubscription interface"""
    return getInterfaceImplementedBy(ISubscription)

def getProviderAllowedContentTypes():
    """Return portal_types implementing ISubscriber interface"""
    return getInterfaceImplementedBy(ISubscriber)
