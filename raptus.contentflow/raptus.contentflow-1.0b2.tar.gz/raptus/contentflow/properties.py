from zope.interface import implements, Interface
from zope.component import adapts

from Products.CMFCore.utils import getToolByName

from raptus.contentflow.interfaces import IContentFlowProperties

class Properties(object):
    """ Provides the properties for a given context
    """
    implements(IContentFlowProperties)
    adapts(Interface)
    
    def __init__(self, context):
        self.context = context
        
    def __call__(self):
        properties = getToolByName(self.context, 'portal_properties').get('raptus_contentflow', None)
        if not properties:
            return []
        return properties.propertyItems()