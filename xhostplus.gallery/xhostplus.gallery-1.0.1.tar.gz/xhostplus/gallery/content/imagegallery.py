"""Definition of the Image Gallery content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from xhostplus.gallery import galleryMessageFactory as _
from xhostplus.gallery.interfaces import IImageGallery
from xhostplus.gallery.config import PROJECTNAME

ImageGallerySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ImageGallerySchema['title'].storage = atapi.AnnotationStorage()
ImageGallerySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ImageGallerySchema,
    folderish=True,
    moveDiscussion=False
)

class ImageGallery(folder.ATFolder):
    """An image gallery folder"""
    implements(IImageGallery)

    meta_type = "Image Gallery"
    schema = ImageGallerySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(ImageGallery, PROJECTNAME)
