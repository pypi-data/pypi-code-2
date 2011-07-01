## Script (Python) "susbcription_csv_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=Exporting subscriptions to content as CSV
##
# $Id: subscription_csv_export.py 227919 2010-12-01 11:43:20Z glenfant $
# -*- coding: utf-8 -*-
filename = 'subscriptions_' + context.getId() + '.csv'
from Products.CMFCore.utils import getToolByName
RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/comma-separated-values; charset=%s' % context.getCharset())
RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + filename)
subscriptions = {}
if context.meta_type=="Plone Site":
    stool = getToolByName(context, 'portal_subscription')
    # In case we are on the root folder, we have to take subscriptions from
    # the portal_subscription tool. Let's hope the Portal site will be
    # an Archetype soon
    subscribers = stool.getBRefs(relationship='subscriptionContentOf')
else
    subscribers = context.getBRefs(relationship='subscriptionContentOf')
for member in subscribers:
    info = member.getSubscriberInfo()
    subscriptions[info['email']]=info['fullname']
if not subscriptions:
    raise "No subscriptions"
# The CSV title line
columns = ['Email','Name']
print ";".join(columns)
# Now all the lines per observation
for subscription in subscriptions.items():
    print ";".join(subscription)
return printed
