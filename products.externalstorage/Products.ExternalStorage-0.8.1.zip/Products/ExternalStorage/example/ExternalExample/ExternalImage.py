from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute

from Products.CMFCore.permissions import View

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import ImageField, ImageWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.public import PrimaryFieldMarshaller

from Products.ExternalStorage.ExternalStorage import ExternalStorage

from Products.ExternalExample.config import ARTICLE_GROUPS, PROJECTNAME

schema = BaseSchema + Schema((

    ImageField('image',
        required = True,
        primary = True,
        swallowResizeExceptions=True,
        storage = ExternalStorage(
            prefix = 'files',
            rename = True,
        ),
        widget = ImageWidget(
            label = 'Image',
            show_content_type=False,
        ),
    ),
    ), marshall=PrimaryFieldMarshaller(),

)


class ExternalImage(BaseContent):
    """This is a sample image, where it and it's scales are stored externally
    """
    
    security = ClassSecurityInfo()

    schema = schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/image_view',
        'permissions': (View,)
        },)

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Make it directly viewable when entering the objects URL
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getPrimaryField()
        data  = field.getAccessor(self)(REQUEST=REQUEST, RESPONSE=RESPONSE)
        if data:
            return data.index_html(REQUEST, RESPONSE)
    
    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return self.tag()

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ZMI / Plone get size method
        """
        img = self.getImage()
        if not getattr(aq_base(img), 'get_size', False):
            return 0
        return img.get_size()

    security.declareProtected(View, 'getSize')
    def getSize(self, scale=None):
        field = self.getField('image')
        return field.getSize(self, scale=scale)

    security.declareProtected(View, 'getWidth')
    def getWidth(self, scale=None):
        return self.getSize(scale)[0]

    security.declareProtected(View, 'getHeight')
    def getHeight(self, scale=None):
        return self.getSize(scale)[1]

    width = ComputedAttribute(getWidth, 1)
    height = ComputedAttribute(getHeight, 1)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None, title=None):
        if file is not None:
            self.setImage(file)
        if title is not None:
            self.setTitle(title)
        self.reindexObject()

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
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return BaseContent.__bobo_traverse__(self, REQUEST, name) 

registerType(ExternalImage, PROJECTNAME)
