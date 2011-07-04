## Script (Python) "addTemplatesProvider"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='subscription_templates'
##title=
##
# -*- coding: utf-8 -*-

url = '%s/view' % context.absolute_url()
psm = "psm_subscriptions_unauthorized"

if not context.portal_membership.checkPermission('View management screens', context):
    return context.REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' % (url, psm))

context.portal_types['TemplatesProvider'].manage_changeProperties(global_allow=True)
context.invokeFactory('TemplatesProvider', id=id)
context.portal_types['TemplatesProvider'].manage_changeProperties(global_allow=False)

psm = 'psm_subscriptions_templates_provider_added'
return context.REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' % (url, psm))
