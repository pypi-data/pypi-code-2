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
