from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.nesting.interfaces import IArticles
from raptus.article.teaser.interfaces import ITeaser

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except:
    pass

class IContentFader(interface.Interface):
    """ Marker interface for the content fader viewlet
    """

class Component(object):
    """ Component which shows a content fader
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Article fader')
    description = _(u'Article fader which continually fades in and out the contained articles.')
    image = '++resource++contentfader.gif'
    interface = IContentFader
    viewlet = 'raptus.article.contentfader'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the content fader
    """
    index = ViewPageTemplateFile('contentfader.pt')
    css_class = "componentFull contentfader-full full"
    thumb_size = "contentfaderthumb"
    img_size = "contentfader"
    component = "contentfader"
    
    @property
    @memoize
    def articles(self):
        provider = IArticles(self.context)
        manageable = interfaces.IManageable(self.context)
        raw_items = manageable.getList(provider.getArticles(component=self.component), self.component)
        items = []
        for item in raw_items:
            img = ITeaser(item['obj'])
            if img.getTeaserURL(self.img_size):
                item.update({'title': item['brain'].Title,
                             'description': item['brain'].Description,
                             'caption': img.getCaption(),
                             'img': img.getTeaser(self.thumb_size),
                             'img_url': img.getTeaserURL(self.img_size),
                             'url': item['brain'].hasDetail and item['brain'].getURL() or None})
                if REFERENCE:
                    reference = IReference(item['obj'])
                    url = reference.getReferenceURL()
                    if url:
                        item['url'] = url
                items.append(item)
        return items

class IContentFaderTeaser(interface.Interface):
    """ Marker interface for the content fader teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a content fader above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Article fader teaser')
    description = _(u'Article fader which continually fades in and out the contained articles and is displayed above the columns.')
    image = '++resource++contentfader_teaser.gif'
    interface = IContentFaderTeaser
    viewlet = 'raptus.article.contentfader.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(Viewlet):
    """ Viewlet showing the content fader
    """
    index = ViewPageTemplateFile('contentfader.pt')
    css_class = "componentFull contentfader-teaser teaser"
    thumb_size = "contentfaderthumb"
    img_size = "contentfaderteaser"
    component = "contentfader.teaser"
