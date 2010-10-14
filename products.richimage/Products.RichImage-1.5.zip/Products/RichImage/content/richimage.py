"""Definition of the RichImage
"""

from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from Products.Archetypes.annotations import getAnnotation
from Products.Archetypes.Storage.annotation import AnnotationStorage

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.base import ATCTFileContent

from Products.RichImage.field import RichImageField
from Products.RichImage.widget import RichImageWidget

from Products.RichImage import RichImageMessageFactory as _
from Products.RichImage.interfaces import IRichImage
from Products.RichImage.config import PROJECTNAME


#override the image field of ATImage with  RichImageField

RichImageSchema = ATContentTypeSchema.copy() + atapi.Schema((
    RichImageField('image',
                   required=True,
                   primary=True,
                   languageIndependent=True,
                   storage = atapi.AnnotationStorage(migrate=True),
                   swallowResizeExceptions = True,
                   pil_quality = zconf.pil_config.quality,
                   pil_resize_algo = zconf.pil_config.resize_algo,
                   max_size = zconf.ATImage.max_image_dimension,
                   sizes = {'large'   : (768, 768),
                            'preview' : (400, 400),
                            'mini'    : (200, 200),
                            'thumb'   : (128, 128),
                            'tile'    :  (64, 64),
                            'icon'    :  (32, 32),
                            'listing' :  (16, 16),
                            },
                   crops = {'frontpage_top'     : (0, 0, 661, 214),
                            'focus'             : (0, 0, 233,  84),
                            'subject_page'      : (0, 0, 485, 214),
                            'person'            : (0, 0, 130, 155),
                            'publication_cover' : (0, 0,  80, 120),
                            'small'             : (0, 0,  80,  80),
                            'page'              : (0, 0, 209, 159),
                            'page_2_columns'    : (0, 0, 458, 159),
                            'content_wide'      : (0, 0, 482, 159),                            
                            'page_wide'         : (0, 0, 707, 159),
                            'category'          : (0, 0, 209, 159),
                            'gallery'           : (0, 0, 209, 209),},
                   createCropsOnSet = False,
                   widget = RichImageWidget(description = '',
                                            label= _(u'label_image',
                                                     default=u'Image'),
                                            show_content_type = False,)),
    atapi.StringField(
        name='photographer',
        schemata = 'default',
        widget=atapi.StringWidget(
            label=_(u"label_image_photographer", default=u"Photographer"),
            description="",
        ),
    ),
    atapi.TextField(
        name='keywords',
        schemata = 'default',
        searchable = True,
        widget=atapi.TextAreaWidget(
            label=_(u"label_image_keywords", default=u"Keywords"),
            description="",
        ),
    ),
    atapi.TextField(
        name='notes',
        schemata = 'default',
        widget=atapi.TextAreaWidget(
            label=_(u"label_image_notes", default=u"Notes"),
            description="",
        ),
    ),
    ))

RichImageSchema['title'].required = False
RichImageSchema['title'].storage = atapi.AnnotationStorage()
RichImageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RichImageSchema, moveDiscussion=False)

RichImageSchema['effectiveDate'].schemata = 'settings'
RichImageSchema['expirationDate'].schemata = 'settings'
RichImageSchema['allowDiscussion'].schemata = 'settings'


class RichImage(ATImage):
    """RichImage content type"""
    implements(IRichImage)

    portal_type = "RichImage"
    schema = RichImageSchema

    security = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the image inline """
        field = self.getPrimaryField()
        return field.index_html(self, REQUEST, RESPONSE)

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return self.tag()

    def available_crops(self):
        """ List of availabe crops for current image """
        field = self.getField('image')
        crops = field.getAvailableCrops(self).keys()

        storage = field.getStorage(self)
        if isinstance(storage, AnnotationStorage):
            annotation = getAnnotation(self)
            key = storage._key
            res = []
            for crop in crops:
                scalename = field.getScaleName(scale=crop)
                if annotation.hasSubkey(key, scalename):
                    res.append(crop)
            return res
        #else:
        #    return [crop for crop in crops if field.getCrop(self, crop=crop)]

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
                if scalename in field.getAvailableCrops(self):
                    image = field.getCrop(self, crop=scalename)
                    if not image:
                        available_crops = field.getAvailableCrops(self)
                        x1, y1, x2, y2 = available_crops[scalename]
                        field._createCrop(self, scalename, x1, y1, x2, y2)
                        image = field.getCrop(self, crop=scalename)                    
                    
                    
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATCTFileContent.__bobo_traverse__(self, REQUEST, name)


atapi.registerType(RichImage, PROJECTNAME)
