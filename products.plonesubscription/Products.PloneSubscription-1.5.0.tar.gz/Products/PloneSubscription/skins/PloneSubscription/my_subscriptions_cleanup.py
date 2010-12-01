## Python Script "my_subscriptions_cleanup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# -*- coding: utf-8 -*-
""" Remove stale subscriptions from various subscriber """

from Products.CMFCore.utils import getToolByName
request = context.REQUEST


sub_tool = context.portal_subscription
subscriber_id = sub_tool.getSubscriberId()

catalog = sub_tool.getCatalog()
search_dict = {}
provider = sub_tool.getProvider()
if provider:
    search_dict['path'] = '%s/%s' % ('/'.join(provider.getPhysicalPath()), subscriber_id)
subscriptions = []
for result in catalog.searchResults(search_dict):
    subscriptions.append(result)


if subscriptions:
    # Remove items that have been deleted
    remove_ids = {}

    for subscription in subscriptions:
        item = subscription.getObject()
        if not item:
            continue
        obj = None
        try:
            obj = context.restrictedTraverse(item.getRpath())
        except:
            pass
        if not obj:
            subscriber = item.getParentNode().UID()
            if remove_ids.has_key(subscriber):
                remove_ids[subscriber].append(item.getId())
            else:
                remove_ids[subscriber] = [item.getId()]
    
    uid_catalog = getToolByName(context, 'uid_catalog')
    for (subscriber_uid, ids) in remove_ids.items():
        subscriber = uid_catalog(UID=subscriber_uid)[0].getObject()
        subscriber.manage_delObjects(ids=ids)
