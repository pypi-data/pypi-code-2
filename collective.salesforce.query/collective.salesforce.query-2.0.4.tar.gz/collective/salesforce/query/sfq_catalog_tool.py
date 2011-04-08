from Products.CMFPlone.CatalogTool import CatalogTool as BaseTool
from Products.ZCatalog.ZCatalog import ZCatalog 
from Products.CMFCore.interfaces import ICatalogTool
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from BTrees.IIBTree import IIBucket


class ISalesforceQueryTool(ICatalogTool):
    """Wrap the "stock" Plone catalog with behavior for 
       remote content cataloging.
    """


class SalesforceQueryTool(BaseTool):
    """ without 
       interference to or from the portal_catalog
    """
    
    id = "portal_sfq_catalog"
    toolicon = 'tool.gif'
    meta_type = 'Salesforce Query Catalog Tool'

    implements(ISalesforceQueryTool)

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        ZCatalog.__init__(self, self.getId())

    def apply_index(self, index, value):
        """ Default portal_catalog index _apply_index
        """
        index_id = index.getId()

        apply_index = getattr(index, '_apply_index', None)
        if not apply_index:
            return IIBucket(), (index_id,)

        rset = apply_index({index_id: value})
        if not rset:
            return IIBucket(), (index_id,)

        return rset

    def search(self, *args, **kwargs):
        """
        I have found that this fails when invoked using faceted navigation product from eea
        So we wrap the search method just in case
        """
        return self(query=kwargs)

