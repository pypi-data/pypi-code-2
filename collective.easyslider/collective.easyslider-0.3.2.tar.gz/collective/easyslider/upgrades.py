from Products.CMFCore.utils import getToolByName
from collective.easyslider.interfaces import ISliderPage

try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations


default_profile = 'profile-collective.easyslider:default'

def upgrade_from_0_3rc1__to__0_3rc2(context):
    context.runImportStepFromProfile(default_profile, 'viewlets')
    context.runImportStepFromProfile(default_profile, 'portlets')
    context.runImportStepFromProfile(default_profile, 'jsregistry')
    context.runImportStepFromProfile(default_profile, 'cssregistry')
    
def upgrade_to_0_3rc2(context):
    #just run all since you don't know what version was previously used
    
    context.runAllImportStepsFromProfile(default_profile)
    

def upgrade_to_0_3rc4(context):
    pass
            
def upgrade_to_0_3(context):
    """
    just reload portal_javascripts for the js changes to take effect
    """
    portal_javascripts = getToolByName(context, 'portal_javascripts')
    portal_javascripts.cookResources()