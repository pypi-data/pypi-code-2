from Products.CMFCore.utils import getToolByName

def uninstall(self):
    ps = getToolByName(self, 'portal_setup')
    ps.runAllImportStepsFromProfile('profile-collective.easyslider:uninstall')
