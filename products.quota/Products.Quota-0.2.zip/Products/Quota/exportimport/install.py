
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Quota import config


def make_quota_aware(context):
    """ instalacion del portal Opimec """
    if context.readDataFile('install_quota.txt') is None:
        return
    out = StringIO()
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    qi.notifyInstalled(config.PRODUCT_NAME)

