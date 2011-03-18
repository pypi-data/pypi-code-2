# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    dict(name='event_types', type_='lines', value=()),
    dict(name='special_event_types', type_='lines', value=()),
    ]

INDEXES_TO_ADD = (
                  ('getEventType','KeywordIndex',{'indexed_attrs': 'getEventType', }),
                  )

def _addKeysToCatalog(portal):
    portal_catalog = portal.portal_catalog

    indexes = portal_catalog.indexes()
    for idx in INDEXES_TO_ADD:
        if idx[0] in indexes:
            print "Found the '%s' index in the catalog, nothing changed." % idx[0]
        else:
            portal_catalog.addIndex(name=idx[0], type=idx[1], extra=idx[2])
            print "Added '%s' (%s) to the catalog." % (idx[0], idx[1])

def import_various(context):
    if context.readDataFile('monet.calendar.event-various.txt') is None:
        return
    # Define portal properties
    site = context.getSite()
    ptool = getToolByName(site, 'portal_properties')
    props = ptool.monet_calendar_event_properties
    
    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])
    
    _addKeysToCatalog(site)
