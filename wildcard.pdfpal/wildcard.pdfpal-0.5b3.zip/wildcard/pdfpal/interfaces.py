from zope import schema
from zope.interface import Interface
from wildcard.pdfpal import mf as _

class ILayer(Interface):
    """
    package layer
    """

class IPDFSettings(Interface):
    """
    PDF Settings
    """
    
    pdf_thumbnails_available = schema.Bool(
        title=u'Thumbnails available',
        default=False
    )
    
class IPDFPalConfiguration(Interface):
    """
    control panel config...
    """
    
    ocr_enabled = schema.Bool(
        title=_(u'OCR Enabled'),
        description=_(u'Enable this if you would like to use OCR for pdf document search results'),
        required=True,
        default=True
    )
    
    thumbnail_gen_enabled = schema.Bool(
        title=_(u'PDF Thumbnails enabled'),
        required=True,
        default=True
    )
    
    preview_width = schema.Int(
        title=_(u'Preview Width'),
        required=True,
        default=512,
    )
    
    preview_height = schema.Int(
        title=_(u'Preview Height'),
        required=True,
        default=512,
    )

    thumbnail_width = schema.Int(
        title=_(u'Thumbnail Width'),
        required=True,
        default=128,
    )

    thumbnail_height = schema.Int(
        title=_(u'Thumbnail Height'),
        required=True,
        default=128,
        )

    