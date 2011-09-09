"""Definition of the goods_image content type
"""

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.image import ATImage

from my315ok.store import storeMessageFactory as _
from my315ok.store.interfaces import Igoods_image
from my315ok.store.config import PROJECTNAME


goods_imageSchema =  ATImage.schema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'link2',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"link to URL"),
            description=_(u"LINK TO URL"),
        ),
        validators=('isURL'),
    ),

    atapi.TextField(
        'comments',
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"image comments"),
            description=_(u"image comments"),
        ),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

goods_imageSchema['title'].storage = atapi.AnnotationStorage()
goods_imageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(goods_imageSchema, moveDiscussion=False)

class goods_image(ATImage):
    """a image of the goods"""
    implements(Igoods_image)

    meta_type = "goods_image"
    schema = goods_imageSchema
   
    _at_rename_after_creation = True
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    link2 = atapi.ATFieldProperty('link2')

    comments = atapi.ATFieldProperty('comments')


atapi.registerType(goods_image, PROJECTNAME)
