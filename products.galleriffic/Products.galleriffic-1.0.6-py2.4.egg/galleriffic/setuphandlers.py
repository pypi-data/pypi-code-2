from Products.CMFPlone.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.ATContentTypes.interface.topic import IATTopic
from Products.galleriffic import PLONE3, PLONE4

def addViewMethod(context):
    site = context.getSite()
    type_tool = getToolByName(site,'portal_types')
    view_types = []
    
    if PLONE3:
        view_types = ['Folder','Topic','Large Plone Folder']
    if PLONE4:
        view_types = ['Folder','Topic']
    
    for view_type in view_types:
        folder_view_methods = list(type_tool[view_type].view_methods)
        if 'galleriffic_view' not in folder_view_methods:
            folder_view_methods.append('galleriffic_view')
            type_tool[view_type].view_methods = tuple(folder_view_methods)