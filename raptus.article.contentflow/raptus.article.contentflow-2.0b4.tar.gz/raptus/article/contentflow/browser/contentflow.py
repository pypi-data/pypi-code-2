from zope import interface, component

from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.teaser.interfaces import ITeaser
from raptus.article.nesting.interfaces import IArticles
from raptus.contentflow.browser.contentflow import Viewlet as ViewletBase
from raptus.contentflow.browser.xml import XML as XMLBase

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except:
    pass

class IContentFlow(interface.Interface):
    """ Marker interface for the content flow viewlet
    """

class Component(object):
    """ Component which shows a content flow
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Coverflow')
    description = _(u'Coverflow showing the contained articles.')
    image = '++resource++contentflow.gif'
    interface = IContentFlow
    viewlet = 'raptus.article.contentflow'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the content flow
    """
    thumb_size = "contentflow"
    component = "contentflow"
    @property
    @memoize
    def properties(self):
        properties = getToolByName(self.context, 'portal_properties').get('raptus_article_%s' % self.component, None)
        if not properties:
            return []
        return dict(properties.propertyItems())

class XML(XMLBase):
    thumb_size = "contentflow"
    component = "contentflow"
    @memoize
    def properties(self):
        properties = getToolByName(self.context, 'portal_properties').get('raptus_article_%s' % self.component, None)
        if not properties:
            return []
        return '\n'.join(['  %s="%s"' % property for property in properties.propertyItems()])
    @memoize
    def items(self):
        provider = IArticles(self.context)
        raw_items = provider.getArticles(component=self.component)
        items = []
        for item in raw_items:
            obj = item.getObject()
            img = ITeaser(obj)
            if img.getTeaserURL(self.thumb_size):
                v = {'title': item.Title,
                     'img': img.getTeaserURL(self.thumb_size),
                     'url': item.hasDetail and item.getURL() or ''}
                if REFERENCE:
                    reference = IReference(obj)
                    url = reference.getReferenceURL()
                    if url:
                        v['url'] = url
                items.append(self.item_template % v)
        return '\n'.join(items)

class IContentFlowTeaser(interface.Interface):
    """ Marker interface for the content fader teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a content fader above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Coverflow teaser')
    description = _(u'Coverflow showing the contained articles and is displayed above the columns.')
    image = '++resource++contentflow_teaser.gif'
    interface = IContentFlowTeaser
    viewlet = 'raptus.article.contentflow.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(Viewlet):
    """ Viewlet showing the content fader
    """
    component = "contentflow.teaser"

class XMLTeaser(XML):
    thumb_size = "contentflowteaser"
    component = "contentflow.teaser"

