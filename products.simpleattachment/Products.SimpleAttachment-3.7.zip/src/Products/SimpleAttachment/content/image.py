from Products.ATContentTypes.content.image import ATImage
from Products.Archetypes.public import registerType
from Products.SimpleAttachment.config import PROJECTNAME

class ImageAttachment(ATImage):
    """An image attachment"""
    portal_type = meta_type = 'ImageAttachment'


registerType(ImageAttachment, PROJECTNAME)
