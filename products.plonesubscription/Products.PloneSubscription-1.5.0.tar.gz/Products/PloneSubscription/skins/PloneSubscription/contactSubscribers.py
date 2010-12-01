## Script (Python) "contactSubscribers"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=subject, message
##title=
##
# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
stool = getToolByName(context, 'portal_subscription')

RESPONSE = context.REQUEST.RESPONSE

url = '%s/view' % context.absolute_url()

emails = {}

if context.meta_type=="Plone Site":
    # In case we are on the root folder, we have to take subscriptions from
    # the portal_subscription tool. Let's hope the Portal site will be
    # an Archetype soon
    members = stool.getBRefs(relationship='subscriptionContentOf')
else:
    members = context.getBRefs(relationship='subscriptionContentOf')

for member in members:
    info = member.getSubscriberInfo()
    emails[info['email']]=1

mtool = getToolByName(context, 'portal_membership')
member = mtool.getAuthenticatedMember()
from_email = member.getProperty('email', None)
if not from_email:
    raise "You don't have your email property set! Go to preferences -> personal preferences"

psm = stool.contactMailing(content = context, emails = emails.keys(), from_email=from_email, subject=subject, message=message)

return RESPONSE.redirect('%s?portal_status_message=%s' % (url, psm))
