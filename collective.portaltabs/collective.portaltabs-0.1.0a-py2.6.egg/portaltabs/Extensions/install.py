# -*- coding: utf-8 -*-

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.setBaselineContext('profile-collective.portaltabs:uninstall')
        setup_tool.runAllImportStepsFromProfile('profile-collective.portaltabs:uninstall')
        try:
            portal.portal_properties.manage_delObjects(ids=['portaltabs_settings'])
        except AttributeError:
            pass