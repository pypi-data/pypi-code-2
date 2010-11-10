import random

from zope import interface, component

try: # Plone 4 and higher
    from Products.ATContentTypes.interfaces.image import IATImage
except: # BBB Plone 3
    from Products.ATContentTypes.interface.image import IATImage

from raptus.article.core.interfaces import IArticle
from raptus.article.images.interfaces import IImages
from raptus.article.randomimage.interfaces import IRandomImage

class RandomImage(object):
    """ Provider for a random image
    """
    interface.implements(IRandomImage)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getImage(self, **kwargs):
        """ Returns a random image (catalog brain)
        """
        provider = IImages(self.context)
        images = provider.getImages(**kwargs)
        if not len(images):
            return None
        return images[random.randint(0, len(images)-1)]
