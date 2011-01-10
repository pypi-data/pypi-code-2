# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import getFSVersionTuple

def install(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-redturtle.imagedevent:default')
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.imagedevent:default')
    if getFSVersionTuple()[0]>=4:
        unregisterIcon(portal)

def uninstall(portal):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-redturtle.imagedevent:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.imagedevent:uninstall')
    if getFSVersionTuple()[0]>=4:
        unregisterIcon(portal)
    return "Ran all uninstall steps."

def unregisterIcon(portal):
    """Remove icon expression from Link type"""
    log = portal.plone_log
    portal_types = portal.portal_types
    event = portal_types.getTypeInfo("Event")
    #link.icon_expr = ''
    event.content_icon = ''
    event.manage_changeProperties(content_icon='', icon_expr='')
    log("Removing icon type info")