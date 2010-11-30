## Script (Python) "lingua_object_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete an object
##

from Products.CMFPlone.utils import base_hasattr

if base_hasattr(context.aq_inner,'myGetTranslations'):
    for translation in context.myGetTranslations():
        translation.plone_object_delete()
else:
    return context.plone_object_delete()
