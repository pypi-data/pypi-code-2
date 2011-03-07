from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from simplelayout.types.common.config import PROJECTNAME
from simplelayout_schemas import textSchema, imageSchema, finalize_simplelayout_schema
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.CMFCore.permissions import View
from simplelayout.types.common.interfaces import IParagraph
from simplelayout.base.interfaces import ISimpleLayoutBlock
from mixinklasses import ImageScalesMixin
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi




schema = atapi.Schema((
     atapi.BooleanField('showTitle',
                schemata='default',
                default=0,
                widget=atapi.BooleanWidget(description = "Show title",
                                             description_msgid = "simplelayout_help_showtitle",
                                             label = "Show Title",
                                             label_msgid = "simplelayout_label_showtitle",
                                             i18n_domain = "simplelayout",
                                             )),   
     atapi.BooleanField('imageClickable',
                schemata='image',
                default=0,
                widget=atapi.BooleanWidget(description = "imageClickable",
                                             description_msgid = "simplelayout_help_imageClickable",
                                             label = "Image Clickable",
                                             label_msgid = "simplelayout_label_imageClickable",
                                             i18n_domain = "simplelayout",
                                             )),   
                                             
     atapi.BooleanField('teaserblock',
                schemata='settings',
                default=0,
                widget=atapi.BooleanWidget(description = "teaser blocks shows their related items (ex. for frontpage)",
                                             description_msgid = "simplelayout_help_teaserblock",
                                             label = "Tick if this block is a teaser",
                                             label_msgid = "simplelayout_label_teaserblock",
                                             i18n_domain = "simplelayout",
                                             )),   
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

paragraph_schema = ATContentTypeSchema.copy() + \
    schema.copy() + textSchema.copy() + imageSchema.copy()

paragraph_schema['excludeFromNav'].default = True
paragraph_schema['title'].required = False
finalize_simplelayout_schema(paragraph_schema)
paragraph_schema['description'].widget.visible = {'edit': 0, 'view': 0}
paragraph_schema['title'].searchable = 0
paragraph_schema.moveField('teaserblock',before="relatedItems")

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Paragraph(ImageScalesMixin,ATDocumentBase):
    """
    """
    security = ClassSecurityInfo()
    implements(ISimpleLayoutBlock, IParagraph)
    schema = paragraph_schema

    # Methods

    #XXX we should use eventhandler
    #special workarround for empty titles, otherwise we have "[...]" 
    #results in the search function
    def setTitle(self, value):
        portal_transforms = getToolByName(self, 'portal_transforms')
        field = self.schema['title']
        if not value:
            #XXX use crop function
            new_value = self.REQUEST.get('text',None)
            if new_value is not None:
                formatted = portal_transforms.convertTo('text/plain', new_value).getData().replace('\r','').replace('\n','')
                cropped = len(formatted) > 30 and formatted[:30] or formatted
                last_space = cropped.rfind(' ')
                if last_space == -1:
                    pass
                else:
                    cropped = cropped[:last_space]
                field.set(self,cropped.lstrip())
        else:
            field.set(self,value)
 

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            if self.getImageAltText():
                kwargs['title'] = self.getImageAltText()
            elif self.getImageCaption():
                kwargs['title'] = self.getImageCaption()
            else:
                kwargs['title'] = self.Title()
        if 'alt' not in kwargs:
            kwargs['alt'] = self.getImageAltText()
        return self.getField('image').tag(self, **kwargs)


    def __bobo_traverse__(self, REQUEST, name):
        """Give transparent access to image scales. This hooks into the
        low-level traversal machinery, checking to see if we are trying to
        traverse to /path/to/object/image_<scalename>, and if so, returns
        the appropriate image content.
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

        return super(Paragraph, self).__bobo_traverse__(REQUEST, name)



atapi.registerType(Paragraph, PROJECTNAME)

