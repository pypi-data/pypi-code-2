from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager

from Products.CMFPlone import PloneMessageFactory as _

class ILogininfoPortlet(IPortletDataProvider):
    """A portlet which can render a login form.
    """

class Assignment(base.Assignment):
    implements(ILogininfoPortlet)

    title = 'login info'

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.membership = getToolByName(self.context, 'portal_membership')

        self.context_state = getMultiAdapter((context, request), name=u'plone_context_state')
        self.portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.pas_info = getMultiAdapter((context, request), name=u'pas_info')
	self.user_actions = self.context_state.actions().get('user', None)
	self.anonymous = self.portal_state.anonymous()
	self.navigation_root_url = self.portal_state.navigation_root_url()
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
	sm = getSecurityManager()
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
	self.site_actions = self.context_state.actions().get('site_actions', None)
	if not self.anonymous:
        
            member = self.portal_state.member()
            userid = member.getId()
            
            if sm.checkPermission('Portlets: Manage own portlets', self.context):
                self.homelink_url = self.navigation_root_url + '/dashboard'
            else:
                self.homelink_url = self.navigation_root_url + \
                    '/personalize_form'
            member_info = tools.membership().getMemberInfo(member.getId())
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid
    render = ViewPageTemplateFile('logininfo.pt')

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
