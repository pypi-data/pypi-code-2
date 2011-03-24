## Script (Python) "dashboard"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##parameters=
##title=Replacement for dashboard page
##
from betahaus.memberprofile import MemberProfileMessageFactory as _

from Products.CMFCore.utils import getToolByName
portal_membership = getToolByName(context, 'portal_membership')

homefolder_url = portal_membership.getHomeUrl()

if homefolder_url:
    context.REQUEST.response.redirect( homefolder_url )
else:
    getToolByName(context, "plone_utils").addPortalMessage(_(u'User profile not available.'))
    context.REQUEST.response.redirect( context.portal_url())
