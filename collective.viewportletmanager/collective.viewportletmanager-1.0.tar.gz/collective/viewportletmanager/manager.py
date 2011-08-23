from ZODB.POSException import ConflictError

from zope.interface import Interface
from zope.component import adapts, getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.memoize.view import memoize
from plone.portlets.manager import logger
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.utils import hashPortletInfo
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.manager import ColumnPortletManagerRenderer

from collective.viewportletmanager.interfaces import IPortletsAwareView


class ViewPortletsManagerRenderer(ColumnPortletManagerRenderer):
    """Override renderer for IPortletsAwareView to pass view object futher
    down to retriever -> contentcontext for it to calculate view key.
    """
    adapts(Interface, IDefaultBrowserLayer, IPortletsAwareView, IColumn)

    @memoize
    def _lazyLoadPortlets(self, manager):
        retriever = getMultiAdapter((self.context, manager), IPortletRetriever)
        items = []
        for p in self.filter(retriever.getPortlets(view=self.__parent__)):
            renderer = self._dataToPortlet(p['assignment'].data)
            info = p.copy()
            info['manager'] = self.manager.__name__
            info['renderer'] = renderer
            hashPortletInfo(info)
            # Record metadata on the renderer
            renderer.__portlet_metadata__ = info.copy()
            del renderer.__portlet_metadata__['renderer']
            try:
                isAvailable = renderer.available
            except ConflictError:
                raise
            except Exception, e:
                isAvailable = False
                logger.exception(
                    "Error while determining renderer availability of portlet "
                    "(%r %r %r): %s" % (
                    p['category'], p['key'], p['name'], str(e)))

            info['available'] = isAvailable
            items.append(info)

        return items

    def portletsToShow(self):
        """Override it to replicate plone4 version in plone3 as well.
        
        Our custom _lazyLoadPortlets method works as in plone4 returning
        even not available portlets in resulting list.
        """
        return [p for p in self._lazyLoadPortlets(self.manager)
            if p['available']]
