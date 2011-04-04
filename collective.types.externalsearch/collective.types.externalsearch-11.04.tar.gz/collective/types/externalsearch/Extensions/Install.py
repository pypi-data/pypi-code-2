import transaction
from Products.CMFCore.utils import getToolByName

PRODUCT_DEPENDENCIES = ('DataGridField',)
EXTENSION_PROFILES = ('collective.types.externalsearch:default',)

def product_install(qi, ps, product, reinstall):
    if reinstall and qi.isProductInstalled(product):
        qi.reinstallProducts([product])
        transaction.savepoint()
    elif not qi.isProductInstalled(product):
        qi.installProduct(product)
        transaction.savepoint()

def products_install(self, reinstall):
    """Install product dependencies"""
    qi = getToolByName(self, 'portal_quickinstaller')
    ps = getToolByName(self, 'portal_setup')

    [product_install(qi, ps, product, reinstall)
     for product in PRODUCT_DEPENDENCIES]

    return

def install(self, reinstall=False):
    """Install this product"""
    #Install product dependencies
    products_install(self, reinstall)
    #portal_setup = getToolByName(self, 'portal_setup')
    #qi = getToolByName(self, 'portal_quickinstaller')

    #Install extension profiles
    extensions_install(self)

def extension_install(self, extension):
    qi = getToolByName(self, 'portal_quickinstaller')
    ps = getToolByName(self, 'portal_setup')

    ps.runAllImportStepsFromProfile('profile-%s' % \
                                    extension,
                                    purge_old=False)
    product_name = extension.split(':')[0]
    qi.notifyInstalled(product_name)
    transaction.savepoint()

def extensions_install(self):
    [extension_install(self, extension)
     for extension in EXTENSION_PROFILES]
    
