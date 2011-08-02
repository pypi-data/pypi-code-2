## Script (Python) "getSplashImage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=splash_type='top_images'
##title=
##
from random import choice
folder = getattr(context, splash_type, None)
if folder:
   image_ids = folder.objectIds()
   if image_ids:
      pcs = folder.aq_inner.aq_parent.restrictedTraverse('@@plone_context_state')
      if pcs.is_portal_root():
         path = '/'.join([context.portal_url(), folder.getId()]) 
      else:      
         path = '/'.join(folder.getPhysicalPath())
      return "%s/%s" % (path, choice(image_ids))
return ""
