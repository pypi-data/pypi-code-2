# -*- coding: utf-8 -*-

def uninstall(portal):
    setup_tool = portal.portal_setup
    setup_tool.setImportContext('profile-experimental.collectionfix8463:uninstall')
    setup_tool.runAllImportSteps()
