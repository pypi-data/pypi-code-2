from collective.plonetruegallery.browser.util import PTGUtility
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
import logging

logging.getLogger('collective.collage.plonetruegallery').warn("Monkey patching collective.plonetruegallery.browser.util.PTGUtility's enabled method.")

@memoize
def enabled(self):
    utils = getToolByName(self.context, 'plone_utils')
    try:
        view_name = utils.browserDefault(self.context)[1][0] 
        return view_name in ["galleryview","collage_view"]
    except:
        return False

PTGUtility.enabled = enabled
