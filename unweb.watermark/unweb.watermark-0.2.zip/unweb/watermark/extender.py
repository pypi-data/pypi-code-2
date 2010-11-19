from Products.Archetypes.public import ImageField
from archetypes.schemaextender.field import ExtensionField
from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import ImageWidget, ComputedField
from Products.ATContentTypes.interface import IATImage
from plone.app.blob.subtypes.image import ExtensionBlobField
from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf

class ExtendedComputedField(ExtensionField, ComputedField):
    """ """
    def getFileSize(self, obj):
        return ImageExtender(obj).fields[0].get_size(obj) or 0L
 
    def getImageSize(self,obj):
        try:
            return ImageExtender(obj).fields[0].getSize(obj)
        except:
            return (0,0)

    def getFilename(self, obj):
        return ImageExtender(obj).fields[0].getFilename(obj) or ''

class ImageExtender(object):
    adapts(IATImage)
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobField("original",
        accessor = 'getOriginal',
        mutator = 'setOriginal',
        languageIndependent = True,
        storage = AnnotationStorage(migrate=True),
        swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
        pil_quality = zconf.pil_config.quality,
        pil_resize_algo = zconf.pil_config.resize_algo,
        sizes={'large'   : (768, 768),},
        read_permission = "unweb.watermark: Download original image",
        write_permission = 'Manage portal',
        widget = ImageWidget(
            label="Original hi-res image",
            visible={'view': 'visible', 'edit': 'invisible' }
            ),
        ),
        ExtendedComputedField("filesize",
        expression="context.Schema().getField('filesize').getFileSize(context)",
        widget = ComputedField._properties['widget'](
            visible={'edit' : 'hidden', 'view':'visible'},
            label='Original file size',
            ),
        ),
        ExtendedComputedField("imagesize",
        expression="context.Schema().getField('filesize').getImageSize(context)",
        widget = ComputedField._properties['widget'](
            visible={'edit' : 'hidden', 'view':'visible'},
            label='Original file size',
            ),
        ),
        ExtendedComputedField("filename",
        expression="context.Schema().getField('filesize').getFilename(context)",
        widget = ComputedField._properties['widget'](
            visible={'edit' : 'hidden', 'view':'visible'},
            label='Original file size',
            ),
        ),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

