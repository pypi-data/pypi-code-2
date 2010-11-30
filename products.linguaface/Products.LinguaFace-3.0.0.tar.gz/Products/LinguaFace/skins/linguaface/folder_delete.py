## Script (Python) "lingua_folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import base_hasattr

paths = context.REQUEST.get('paths', [])
portal = context.portal_url.getPortalObject()
REQUEST = context.REQUEST

if not paths:
    return context.plone_folder_delete()

for path in paths:
    obj = portal.restrictedTraverse(path)
    if base_hasattr(obj.aq_inner,'myGetTranslations'):
        for translation in obj.myGetTranslations():
            REQUEST.set('paths', ['/'.join(translation.getPhysicalPath())])
            translation.aq_inner.aq_parent.plone_folder_delete()
    else:
        return context.plone_folder_delete()


context.plone_utils.addPortalMessage(_(u'Item(s) deleted.'))
