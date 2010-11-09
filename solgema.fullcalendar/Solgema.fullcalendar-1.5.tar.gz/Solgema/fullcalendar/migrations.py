import transaction
from Products.CMFCore.utils import getToolByName
from Solgema.fullcalendar.config import PRODUCT_DEPENDENCIES

def doNothing(context):
    pass

def upgrade03(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')

    for product in PRODUCT_DEPENDENCIES:
        if not portal_quickinstaller.isProductInstalled(product):
            try:
                portal_quickinstaller.installProduct(product)
            except:
                pass
            transaction.savepoint()

def upgrade11(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')

    for product in PRODUCT_DEPENDENCIES:
        if not portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.installProduct(product)
            transaction.savepoint()

    jstool = getToolByName(context, 'portal_javascripts')
    jstool.cookResources()
    csstool = getToolByName(context, 'portal_css')
    csstool.cookResources()

def upgrade12(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')

    portal_setup.runAllImportStepsFromProfile('profile-Solgema.fullcalendar:upgrade12', purge_old=False)

    jstool = getToolByName(context, 'portal_javascripts')
    jstool.cookResources()
    csstool = getToolByName(context, 'portal_css')
    csstool.cookResources()

def upgrade13(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')

    portal_setup.runAllImportStepsFromProfile('profile-Solgema.fullcalendar:upgrade13', purge_old=False)

    jstool = getToolByName(context, 'portal_javascripts')
    jstool.cookResources()
    csstool = getToolByName(context, 'portal_css')
    csstool.cookResources()

def upgrade14(context):
    jstool = getToolByName(context, 'portal_javascripts')
    jstool.cookResources()
