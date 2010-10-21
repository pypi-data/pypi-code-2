from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

try: # Plone 4 and higher
    from Products.ATContentTypes.interfaces.image import IATImage
except: # BBB Plone 3
    from Products.ATContentTypes.interface.image import IATImage

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.images.interfaces import IImage
from raptus.article.randomimage.interfaces import IRandomImage

class IRandomImageLeft(interface.Interface):
    """ Marker interface for the random image left viewlet
    """

class ComponentLeft(object):
    """ Component which shows a random image on the left side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random image left')
    description = _(u'Random image on the left side.')
    image = '++resource++randomimage_left.gif'
    interface = IRandomImageLeft
    viewlet = 'raptus.article.randomimage.left'
    
    def __init__(self, context):
        self.context = context

class ViewletLeft(ViewletBase):
    """ Viewlet showing a random image of an article on the left side
    """
    index = ViewPageTemplateFile('randomimage.pt')
    css_class = "componentLeft randomimage-left"
    thumb_size = "randomimageleft"
    component = "randomimage.left"
    
    @property
    @memoize
    def item(self):
        provider = IRandomImage(self.context)
        manageable = interfaces.IManageable(self.context)
        image = provider.getImage(component=self.component)
        if not image:
            return None
        items = manageable.getList([image,], self.component)
        item = items[0]
        provider = IImage(item['obj'])
        item.update({'caption': provider.getCaption(),
                     'tag': provider.getImage(size=self.thumb_size),
                     'url': None})
        w, h = item['obj'].getSize()
        pw, ph = provider.getSize(size="popup")
        tw, th = provider.getSize(self.thumb_size)
        if ((tw < w and tw > 0) or (th < h and th > 0)) and (tw < pw and th < ph):
            item['url'] = provider.getImageURL(size="popup")
        return item

class IRandomImageRight(interface.Interface):
    """ Marker interface for the random image right viewlet
    """

class ComponentRight(object):
    """ Component which shows a random image on the right side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random image right')
    description = _(u'Random image on the right side.')
    image = '++resource++randomimage_right.gif'
    interface = IRandomImageRight
    viewlet = 'raptus.article.randomimage.right'
    
    def __init__(self, context):
        self.context = context

class ViewletRight(ViewletLeft):
    """ Viewlet showing a random image on the right side
    """
    css_class = "componentRight randomimage-right"
    thumb_size = "randomimageright"
    component = "randomimage.right"

class IRandomImageFull(interface.Interface):
    """ Marker interface for the random image full viewlet
    """

class ComponentFull(object):
    """ Component which shows a random image over the whole width
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random image')
    description = _(u'Random image over the whole width.')
    image = '++resource++randomimage_full.gif'
    interface = IRandomImageFull
    viewlet = 'raptus.article.randomimage.full'
    
    def __init__(self, context):
        self.context = context

class ViewletFull(ViewletLeft):
    """ Viewlet showing a random image over the whole width
    """
    css_class = "componentFull randomimage-full"
    thumb_size = "randomimagefull"
    component = "randomimage.full"

class IRandomImageTeaser(interface.Interface):
    """ Marker interface for the random image teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a random image over the whole width displayed above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Random image teaser')
    description = _(u'Random image over the whole width and displayed above the columns.')
    image = '++resource++randomimage_teaser.gif'
    interface = IRandomImageTeaser
    viewlet = 'raptus.article.randomimage.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(ViewletLeft):
    """ Viewlet showing a random image over the whole width displayed above the columns
    """
    css_class = "componentFull"
    thumb_size = "randomimageteaser"
    component = "randomimage.teaser"
