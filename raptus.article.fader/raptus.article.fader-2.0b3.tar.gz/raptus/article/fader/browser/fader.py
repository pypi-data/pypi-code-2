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
from raptus.article.images.interfaces import IImages, IImage

class IFaderFull(interface.Interface):
    """ Marker interface for the image fader full viewlet
    """

class ComponentFull(object):
    """ Component which shows an image fader over the whole width
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Image fader')
    description = _(u'Image fader over the whole width which continually fades in and out the images contained in the article.')
    image = '++resource++fader_full.gif'
    interface = IFaderFull
    viewlet = 'raptus.article.fader.full'
    
    def __init__(self, context):
        self.context = context

class ViewletFull(ViewletBase):
    """ Viewlet showing the image fader over the whole width
    """
    index = ViewPageTemplateFile('fader.pt')
    css_class = "componentFull imagefader-full"
    img_size = "faderfull"
    component = "fader.full"
    
    @property
    @memoize
    def images(self):
        items = []
        provider = IImages(self.context)
        images = provider.getImages(component=self.component)
        for image in images:
            obj = image.getObject()
            img = IImage(obj)
            item = {'caption': img.getCaption(),
                    'img': img.getImageURL(self.img_size),}
            items.append(item)
        return items

class IFaderLeft(interface.Interface):
    """ Marker interface for the image fader left viewlet
    """

class ComponentLeft(object):
    """ Component which shows an image fader on the left side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Image fader left')
    description = _(u'Image fader on the left side which continually fades in and out the images contained in the article.')
    image = '++resource++fader_left.gif'
    interface = IFaderLeft
    viewlet = 'raptus.article.fader.left'
    
    def __init__(self, context):
        self.context = context

class ViewletLeft(ViewletFull):
    """ Viewlet showing the image fader on the left side
    """
    index = ViewPageTemplateFile('fader.pt')
    css_class = "componentLeft imagefader-left"
    img_size = "faderleft"
    component = "fader.left"

class IFaderRight(interface.Interface):
    """ Marker interface for the image fader right viewlet
    """

class ComponentRight(object):
    """ Component which shows an image fader on the right side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Image fader right')
    description = _(u'Image fader on the right side which continually fades in and out the images contained in the article.')
    image = '++resource++fader_right.gif'
    interface = IFaderRight
    viewlet = 'raptus.article.fader.right'
    
    def __init__(self, context):
        self.context = context

class ViewletRight(ViewletFull):
    """ Viewlet showing the image fader on the right side
    """
    index = ViewPageTemplateFile('fader.pt')
    css_class = "componentRight imagefader-right"
    img_size = "faderright"
    component = "fader.right"

class IFaderTeaser(interface.Interface):
    """ Marker interface for the image fader teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows an image fader above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Image fader teaser')
    description = _(u'Image fader over the whole width which continually fades in and out the images contained in the article and is displayed above the columns.')
    image = '++resource++fader_teaser.gif'
    interface = IFaderTeaser
    viewlet = 'raptus.article.fader.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(ViewletFull):
    """ Viewlet showing the image fader above the columns
    """
    index = ViewPageTemplateFile('fader.pt')
    css_class = "componentFull imagefader-teaser"
    img_size = "faderteaser"
    component = "fader.teaser"
