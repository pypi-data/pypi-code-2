from Products.CMFCore.utils import getToolByName


def v2(context):
    context.runImportStepFromProfile('profile-collective.js.fullcalendar:default',
                                     'jsregistry', run_dependencies=False,
                                     purge_old=False)
    getToolByName(context, 'portal_javascripts').cookResources()