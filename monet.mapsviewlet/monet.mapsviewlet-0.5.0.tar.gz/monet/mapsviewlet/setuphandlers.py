# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    dict(name='googlemaps_key', type_='lines', value=["http://localhost:8080 | ABQIAAAANBYEg19BJ5hTrQYvwxEowBTwM0brOpm",]),
]


def setupVarious(context):
    portal = context.getSite()
    if context.readDataFile('monet.mapsviewlet_various.txt') is None: 
        return

    site = context.getSite()
    # Define portal properties
    ptool = getToolByName(site, 'portal_properties')
    props = ptool.monet_properties

    if props:
        for prop in _PROPERTIES:
            if not props.hasProperty(prop['name']):
                props.manage_addProperty(prop['name'], prop['value'], prop['type_'])
                print "Added %s property" % prop['name']
            else:
                print "Property %s already exists. Doing nothing." % prop['name']
