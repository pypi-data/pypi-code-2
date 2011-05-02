try:
    #plone4
    from App.class_init import InitializeClass
except ImportError:
    #plone3
    from Globals import InitializeClass

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.utils import ImportConfiguratorBase
from Products.GenericSetup.utils import CONVERTER, DEFAULT, KEY
#
#   Configurator entry points
#
_FILENAME = 'products.xml'


def importProducts(context):
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    encoding = context.getEncoding()
    logger = context.getLogger('products')

    text = context.readDataFile(_FILENAME)

    if text is not None:

        rc = ProductsImportConfigurator(site, encoding)
        products_info = rc.parseXML(text)

        for product in products_info['installs']:
            qi.installProduct(product)

    logger.info('Products imported.')


class ProductsImportConfigurator(ImportConfiguratorBase):

    """ Synthesize XML description of sitewide role-permission settings.
    """
    security = ClassSecurityInfo()

    def _getImportMapping(self):

        return {
          'products':
            {'installs': {CONVERTER: self._convertToUnique, DEFAULT: ()},
               },
          'installs':
            {'product': {KEY: None}},
          'product':
            {'name': {KEY: None}},
           }

InitializeClass(ProductsImportConfigurator)
