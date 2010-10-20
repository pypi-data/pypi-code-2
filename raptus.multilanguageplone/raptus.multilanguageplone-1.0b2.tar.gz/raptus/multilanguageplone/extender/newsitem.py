from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.newsitem import ATNewsItem

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class NewsItemExtender(DefaultExtender):
    adapts(ATNewsItem)

    fields = DefaultExtender.fields + [
        fields.TextField('text',
            required = False,
            searchable = True,
# we got an error with this attribute on Plone 3.3
# Tried to add 'text___fr___' as primary field but <Products.Archetypes.Schema.Schema object at 0x0AE1BBD0> already has the primary field 'text'
#
# we need the primary markers to have the getContentType method working
            primary=True,
            storage = AnnotationStorage(migrate=True),
            default_output_type = 'text/x-html-safe',
            widget = widgets.RichWidget(
                description = '',
                label = _(u'label_body_text', u'Body Text'),
                rows = 25,
                allow_file_upload = zconf.ATDocument.allow_document_upload
            ),
            schemata='default',
        ),
        fields.ImageField('image',
            required = False,
            storage = AnnotationStorage(migrate=True),
            languageIndependent = True,
            max_size = zconf.ATNewsItem.max_image_dimension,
            sizes= {'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :  (64, 64),
                    'icon'    :  (32, 32),
                    'listing' :  (16, 16),
                   },
            widget = widgets.ImageWidget(
                description = _(u'help_news_image', default=u'Will be shown in the news listing, and in the news item itself. Image will be scaled to a sensible size.'),
                label= _(u'label_news_image', default=u'Image'),
                show_content_type = False
            )
        ),
        fields.StringField('imageCaption',
            required = False,
            searchable = True,
            widget = widgets.StringWidget(
                description = '',
                label = _(u'label_image_caption', default=u'Image Caption'),
                size = 40
            )
        ),
    ]

# monkeypatch to support access to multilanguage image scales
def __bobo_traverse__(self, REQUEST, name):
    """Transparent access to multilanguage image scales
    """
    if name.startswith('image'):
        field = self.getField('image')
        image = None
        if name == 'image':
            image = field.getScale(self)
        elif '___' in name:
            name, lang, scalename = name.split('___')
            if scalename:
                scalename = scalename[1:]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename, lang=lang)
            else:
                image = field.getScale(self, lang=lang)
        else:
            scalename = name[len('image_'):]
            if scalename in field.getAvailableSizes(self):
                image = field.getScale(self, scale=scalename)
        if image is not None and not isinstance(image, basestring):
            # image might be None or '' for empty images
            return image

    return ATDocumentBase.__bobo_traverse__(self, REQUEST, name)
ATNewsItem.__bobo_traverse__ = __bobo_traverse__