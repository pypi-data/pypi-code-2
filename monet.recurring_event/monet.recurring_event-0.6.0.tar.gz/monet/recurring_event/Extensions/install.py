# -*- coding: utf-8 -*-

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.setImportContext('profile-monet.recurring_event:uninstall')
        setup_tool.runAllImportSteps()