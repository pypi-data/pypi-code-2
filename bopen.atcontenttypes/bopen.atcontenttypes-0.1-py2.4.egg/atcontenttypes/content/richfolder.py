"""Definition of the RichFolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf

# -*- Message Factory Imported Here -*-
from bopen.atcontenttypes import atcontenttypesMessageFactory as _

from bopen.atcontenttypes.interfaces import IRichFolder, IHaveLongDescription
from bopen.atcontenttypes.interfaces.longdescription import IHaveLongDescription as Z2IHaveLongDescription
from bopen.atcontenttypes.config import PROJECTNAME

RichFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        'long_description',
        searchable=True,
        storage=atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u"Long Description"),
            description=_(u"Will be shown befor the content body and where long descriptions are needed"),
            rows=10,
        ),
    ),

    atapi.TextField('text',
        required=False,
        searchable=True,
        primary=True,
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
            description = '',
            label = _(u'label_body_text', default=u'Body Text'),
            rows = 25,
            allow_file_upload = zconf.ATDocument.allow_document_upload),
    ),

    atapi.ImageField(
        'content_logo',
        original_size=(128, 128),
        sizes={
            'micro': (16, 32),
            'mini': (32, 64),
            'normal': (64, 128),
        },
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Content Image"),
            description=_(u"Field description"),
        ),
        validators=('isNonEmptyFile'),
    ),

    atapi.BooleanField('dont_link_to_contents',
        default = False,
        required = False,
        languageIndependent = True,
        storage=atapi.AnnotationStorage(),
        widget = atapi.BooleanWidget(
            label= _(
                u'help_label_dont_link_to_contents',
                default=u'Don\'t link to contents'),
            description = _(
                u'help_description_dont_link_to_contents',
                default=u'If selected, this will avoid users the ability to click the contents of the folder.')
            ),
    ),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

RichFolderSchema['title'].storage = atapi.AnnotationStorage()
RichFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    RichFolderSchema,
    folderish=True,
    moveDiscussion=False
)
RichFolderSchema.changeSchemataForField('dont_link_to_contents', 'settings')

class RichFolder(folder.ATFolder):
    """A rich folder"""
    implements(IRichFolder, IHaveLongDescription)
    __implements__ = (getattr(folder.ATFolder,'__implements__',()),) + (Z2IHaveLongDescription,)
    meta_type = "RichFolder"
    schema = RichFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    content_logo = atapi.ATFieldProperty('content_logo')
    long_description = atapi.ATFieldProperty('long_description')
    dont_link_to_contents = atapi.ATFieldProperty('dont_link_to_contents')
    text = atapi.ATFieldProperty('text')
    # workaround to make resized images:
    # the problem is described on http://plone.293351.n2.nabble.com/ImageField-AttributeStorage-and-Max-Recursion-Depth-Error-td4447134.html
    # so, applied the workaround on http://www.seantis.ch/news/blog/archive/2009/06/22/archetypes-annotationstorage-and-image-scaling
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('content_logo'):
            field = self.getField('content_logo')
            image = None
            if name == 'content_logo':
                image = field.getScale(self)
            else:
                scalename = name[len('content_logo_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return folder.ATFolder.__bobo_traverse__(self, REQUEST, name)

    def content_logo_tag(self, **kwargs):
        """
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.Description()
        logo_field = self.getField('content_logo')
        return logo_field.tag(self, **kwargs)

atapi.registerType(RichFolder, PROJECTNAME)
