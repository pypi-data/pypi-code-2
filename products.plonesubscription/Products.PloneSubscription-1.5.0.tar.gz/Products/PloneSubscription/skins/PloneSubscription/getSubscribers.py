## Script (Python) "getSubscribers"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch=False,b_size=50
##title=
##
from Products.CMFCore.utils import getToolByName
portal=context.portal_url.getPortalObject()
subCatalog = getToolByName(portal, 'subscription_catalog')
mtool = getToolByName(portal, 'portal_membership')
subProvider=portal.subscription_provider
subscribersIds=subProvider.objectIds()
results=[]
for subscriber_id in subscribersIds :
    try:
       member = mtool.getMemberById(subscriber_id)
    except:
       continue
    if member:
        email = member.getProperty('email','')
        fullname = member.getProperty('fullname',subscriber_id)
        results.append({'id':subscriber_id,
                        'email':email,
                        'fullname': fullname})

results.sort( lambda x, y: cmp( x['fullname'], y['fullname'] ) )
                    
if batch:
    from Products.CMFPlone import Batch
    b_start = context.REQUEST.get('b_start', 0)
    batch = Batch(results, b_size, int(b_start), orphan=0)
    return batch                    
return results

