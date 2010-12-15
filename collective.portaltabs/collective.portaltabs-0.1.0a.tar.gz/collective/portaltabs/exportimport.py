# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    dict(name='manageable_categories', type_='lines', value=('portal_tabs|Portal tabs')),
    ]

def import_various(context):
    if context.readDataFile('collective.portaltabs-various.txt') is None:
        return
    # Define portal properties
    site = context.getSite()
    ptool = getToolByName(site, 'portal_properties')
    props = ptool.portaltabs_settings
    
    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])