import re

from zope.interface import implements, Interface
from zope.component import adapts, queryAdapter

from Products.ATContentTypes.content.topic import ATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import safe_callable

from raptus.contentflow.interfaces import IContentFlowBrainProvider, IContentFlowProvider

class Topic(object):
    """ Provides brains for content flow displayed in a topic
    """
    implements(IContentFlowBrainProvider)
    adapts(ATTopic)
    
    def __init__(self, context):
        self.context = context
        
    def __call__(self):
        return self.context.queryCatalog()
    
class Folder(object):
    """ Provides brains for content flow displayed in a folder
    """
    implements(IContentFlowBrainProvider)
    adapts(IFolderish)
    
    def __init__(self, context):
        self.context = context
        
    def __call__(self):
        return self.context.getFolderContents()

class Provider(object):
    """ Provides the items to display for a given context
    """
    implements(IContentFlowProvider)
    adapts(Interface)
    
    def __init__(self, context):
        self.context = context
        
    def __call__(self):
        provider = queryAdapter(self.context, interface=IContentFlowBrainProvider)
        if not provider:
            return None
        results = provider()
        use_view_action = getToolByName(self.context, 'portal_properties').site_properties.getProperty('typesUseViewActionInListings', ())
        items = []
        for brain in results:
            object = brain.getObject()
            tag = getattr(object, 'tag', None)
            if not tag or not safe_callable(tag):
                continue
            tag = tag(scale='preview', css_class='content')
            if not tag:
                continue
            name = re.search('src="[^"]*\/([^"^\/]*)_preview"', tag).group(1)
            image = object.getField(name).get(object)
            if not image or not image.get_size():
                continue
            items.append({'img': '%s/%s_preview' % (object.absolute_url(), name),
                          'title': brain.Title,
                          'url': brain.portal_type in use_view_action and '%s/view' % object.absolute_url() or object.absolute_url()})
        return items
