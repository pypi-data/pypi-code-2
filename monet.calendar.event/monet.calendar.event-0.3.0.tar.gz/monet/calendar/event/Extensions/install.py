# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import getFSVersionTuple

def install(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-monet.calendar.event:default')
    setup_tool.runAllImportStepsFromProfile('profile-monet.calendar.event:default')
    if getFSVersionTuple()[0]>=4:
        unregisterIcon(portal)

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.setBaselineContext('profile-monet.calendar.event:uninstall')
        setup_tool.runAllImportStepsFromProfile('profile-monet.calendar.event:uninstall')
        setup_tool.runAllImportSteps()
    if getFSVersionTuple()[0]>=4:
        unregisterIcon(portal)

def unregisterIcon(portal):
    """Remove icon expression from Event type"""
    log = portal.plone_log
    portal_types = portal.portal_types
    t = portal_types.getTypeInfo("Event")
    #t.icon_expr = ''
    if t:
        t.content_icon = ''
        t.manage_changeProperties(content_icon='', icon_expr='')
        log("Removing icon type info")

