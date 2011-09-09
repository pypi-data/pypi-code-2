from zope.interface import implements, Interface

from Products.Five import BrowserView
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from my315ok.store import storeMessageFactory as _


class Igoods_image_View(Interface):
    """
    goods_image_ view interface
    """

    def test():
        """ test method"""


class goods_image_View(BrowserView):
    """
    goods_image_ browser view
    """
    implements(Igoods_image_View)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @memoize
    def img_tag(self,fieldname='image',scale='thumb'):

        fd = self.context.getField(fieldname)
        return fd.tag(self.context,scale=scale)

    @memoize
    def parentobjurl(self):
        parent = self.context.aq_inner.aq_parent
        return parent.absolute_url()
        

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
