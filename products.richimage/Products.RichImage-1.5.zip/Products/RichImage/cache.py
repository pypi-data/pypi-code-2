from zope.component import adapts
from zope.interface import implements
from Products.CacheSetup.interfaces import IPurgeUrls
from Products.CMFCore.utils import getToolByName
from Products.RichImage.interfaces import IRichImage


class RichImagePurge(object):
    """CacheSetup purge helper.

    This adapter adds the URLs for all available crops to the list of URLs
    to purge.
    """
    adapts(IRichImage)
    implements(IPurgeUrls)

    def __init__(self, context):
        self.context=context

    def getRelativeUrls(self):
        urltool=getToolByName(self.context, "portal_url")
        base=urltool.getRelativeUrl(self.context)
        crops=self.context.getField("image").getAvailableCrops(self.context).keys()
        return ["%s/%s" % (base, crop) for crop in crops]

    def getAbsoluteUrls(self, relative_urls):
        return []
