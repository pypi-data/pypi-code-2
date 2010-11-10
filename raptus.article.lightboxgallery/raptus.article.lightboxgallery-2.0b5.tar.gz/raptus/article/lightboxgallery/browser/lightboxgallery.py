from Acquisition import aq_inner
from zope import interface, component

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

class ILightboxGallery(interface.Interface):
    """ Marker interface for the lightbox gallery viewlet
    """

class Component(object):
    """ Component which shows a lightbox gallery of the images
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Lightbox with gallery')
    description = _(u'Lightbox of the images contained in the article including a horizontal gallery.')
    image = '++resource++lightboxgallery.gif'
    interface = ILightboxGallery
    viewlet = 'raptus.article.lightboxgallery'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the lightbox gallery of the images
    """
    index = ViewPageTemplateFile('lightboxgallery.pt')
    css_class = "componentFull"
    thumb_size = "lightboxgallerythumb"
    img_size = "lightboxgallery"
    component = "lightboxgallery"
    
    @property
    @memoize
    def images(self):
        provider = IImages(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getImages(component=self.component), self.component)
        for item in items:
            img = IImage(item['obj'])
            item.update({'caption': img.getCaption(),
                         'img': img.getImage(self.thumb_size),
                         'url': img.getImageURL(self.img_size)})
        return items
