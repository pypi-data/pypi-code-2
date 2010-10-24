from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.randomcontent.interfaces import IRandomContent

TEASER = False
try:
    from raptus.article.teaser.interfaces import ITeaser
    TEASER = True
except:
    pass

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except:
    pass

class IRandomContentLeft(interface.Interface):
    """ Marker interface for the random content left viewlet
    """

class ComponentLeft(object):
    """ Component which shows a random article with the image on the left side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random article left')
    description = _(u'Random article with it\'s image displayed on the left side.')
    image = '++resource++randomcontent_left.gif'
    interface = IRandomContentLeft
    viewlet = 'raptus.article.randomcontent.left'
    
    def __init__(self, context):
        self.context = context

class ViewletLeft(ViewletBase):
    """ Viewlet showing a random article with the image on the left side
    """
    index = ViewPageTemplateFile('randomcontent.pt')
    thumb_size = "randomcontentleft"
    component = "randomcontent.left"
    image_class = "componentLeft"
    type = "left"
    
    @property
    def title_pre(self):
        props = getToolByName(self.context, 'portal_properties').raptus_article
        return props.getProperty('randomcontent_%s_titletop' % self.type, False)
    
    @property
    @memoize
    def article(self):
        provider = IRandomContent(self.context)
        manageable = interfaces.IManageable(self.context)
        article = provider.getArticle(component=self.component)
        if not article:
            return None
        items = manageable.getList([article,], self.component)
        item = items[0]
        item.update({'title': item['brain'].Title,
                     'description': item['brain'].Description,
                     'url': item['brain'].hasDetail and item['brain'].getURL() or None})
        if REFERENCE:
            reference = IReference(item['obj'])
            url = reference.getReferenceURL()
            if url:
                item['url'] = url
        if TEASER:
            teaser = ITeaser(item['obj'])
            image = {'img': teaser.getTeaser(self.thumb_size),
                     'caption': teaser.getCaption(),
                     'url': None,
                     'rel': None}
            if image['img']:
                w, h = item['obj'].Schema()['image'].getSize(item['obj'])
                tw, th = teaser.getSize(self.thumb_size)
                if item['url']:
                    image['url'] = item['url']
                elif (tw < w and tw > 0) or (th < h and th > 0):
                    image['rel'] = 'lightbox'
                    image['url'] = teaser.getTeaserURL(size="popup")
                item['image'] = image
        return item

class IRandomContentRight(interface.Interface):
    """ Marker interface for the random content right viewlet
    """

class ComponentRight(object):
    """ Component which shows a random article with the image on the right side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random article right')
    description = _(u'Random article with it\'s image displayed on the right side.')
    image = '++resource++randomcontent_right.gif'
    interface = IRandomContentRight
    viewlet = 'raptus.article.randomcontent.right'
    
    def __init__(self, context):
        self.context = context

class ViewletRight(ViewletLeft):
    """ Viewlet showing a random article with the image on the right side
    """
    thumb_size = "randomcontentright"
    component = "randomcontent.right"
    image_class = "componentRight"
    type = "right"

class IRandomContentFull(interface.Interface):
    """ Marker interface for the random content full viewlet
    """

class ComponentFull(object):
    """ Component which shows a random article with the image over the whole width
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random article')
    description = _(u'Random article with it\'s image displayed over the whole width.')
    image = '++resource++randomcontent_full.gif'
    interface = IRandomContentFull
    viewlet = 'raptus.article.randomcontent.full'
    
    def __init__(self, context):
        self.context = context

class ViewletFull(ViewletLeft):
    """ Viewlet showing a random article with the image over the whole width
    """
    thumb_size = "randomcontentfull"
    component = "randomcontent.full"
    image_class = "componentFull"
    type = "full"

class IRandomContentTeaser(interface.Interface):
    """ Marker interface for the random content teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a random article with the image over the whole width displayed above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random article teaser')
    description = _(u'Random article with it\'s image displayed over the whole width and displayed above the columns.')
    image = '++resource++randomcontent_teaser.gif'
    interface = IRandomContentTeaser
    viewlet = 'raptus.article.randomcontent.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(ViewletLeft):
    """ Viewlet showing a random article with the image over the whole width displayed above the columns
    """
    thumb_size = "randomcontentteaser"
    component = "randomcontent.teaser"
    image_class = "componentFull"
    type = "teaser"
