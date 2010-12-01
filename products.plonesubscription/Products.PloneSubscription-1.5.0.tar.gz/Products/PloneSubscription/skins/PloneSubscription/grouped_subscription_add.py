## Script (Python) "grouped_subscription_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# -*- coding: utf-8 -*-

""" Add the subscription for each subcriber passed in parameters """

kw = {}
if context.REQUEST:
    kw.update(context.REQUEST.form)

for subscriber_uid in kw.get('groupSubscriber', []):
    context.addSubscription(ptype='FolderSubscription', subscriber_uid=subscriber_uid)

return True
