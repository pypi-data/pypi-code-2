# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import getFSVersionTuple

def install(portal, reinstall=False):
    if getFSVersionTuple()[1]<=2:
        setup_tool = portal.portal_setup
        setup_tool.setBaselineContext('profile-experimental.collectionfix8463:default_32')
        setup_tool.runAllImportStepsFromProfile('profile-experimental.collectionfix8463:default_32')
        portal.plone_log("experimental.collectionfix8463: installed layer for Plone 3.2")
    else:
        setup_tool = portal.portal_setup
        setup_tool.setBaselineContext('profile-experimental.collectionfix8463:default_33')
        setup_tool.runAllImportStepsFromProfile('profile-experimental.collectionfix8463:default_33')
        portal.plone_log("experimental.collectionfix8463: installed layer for Plone 3.3")

def uninstall(portal):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-experimental.collectionfix8463:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-experimental.collectionfix8463:uninstall')
    portal.plone_log("experimental.collectionfix8463: removed layers")
