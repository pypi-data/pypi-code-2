# -*- coding: utf-8 -*-

from Acquisition import aq_base
from zope.interface import implements, Interface
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

from AccessControl.SecurityManagement import newSecurityManager

class ICollectionProxyView(IBrowserView):
    """
    ContentProxy view interface
    """


class CollectionProxyView(BrowserView):
    """
    ContentProxy browser view
    """
    implements(ICollectionProxyView)
        
    def get_item_url(self, item):
        """
        """
        if hasattr(self.context, 'boolean_proxy_field') and self.context.boolean_proxy_field:
            return self.context.absolute_url()+u'/»'+item.getPath()
        elif hasattr(item, 'getURL'):
            return item.getURL()
        else:
            return item.absolute_url();

