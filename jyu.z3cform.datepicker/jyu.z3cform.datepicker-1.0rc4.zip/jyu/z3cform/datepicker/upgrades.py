# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName


def upgrade1to2(self):
    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(\
        'profile-jyu.z3cform.datepicker:upgrade1to2')
    return u"Upgraded jyu.z3cform.datepicker GenericSetup profile from 1 to 2."


def upgrade2to3(self):
    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(\
        'profile-jyu.z3cform.datepicker:upgrade2to3')
    return u"Upgraded jyu.z3cform.datepicker GenericSetup profile from 2 to 3."
