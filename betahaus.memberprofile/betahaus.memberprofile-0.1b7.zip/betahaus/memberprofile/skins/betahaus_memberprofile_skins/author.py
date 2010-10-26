## Script (Python) "author"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Replacement for author page
##
from betahaus.memberprofile import MemberProfileMessageFactory as _

from Products.CMFCore.utils import getToolByName
portal_membership = getToolByName(context, 'portal_membership')

if not traverse_subpath:
    homefolder_url = portal_membership.getHomeUrl()
else:
    homefolder_url = portal_membership.getHomeUrl(traverse_subpath[0])

if homefolder_url:
    context.REQUEST.response.redirect( homefolder_url )
else:
    getToolByName(context, "plone_utils").addPortalMessage(_(u'User profile not available.'))
    context.REQUEST.response.redirect( context.portal_url())
    
