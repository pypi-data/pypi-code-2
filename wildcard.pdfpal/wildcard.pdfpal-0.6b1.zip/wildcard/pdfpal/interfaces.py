from zope import schema
from zope.interface import Interface
from wildcard.pdfpal import mf as _
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

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
        description=_(u'Enable this if you would like to use OCR for pdf document search results.'),
        required=True,
        default=True
    )
    
    overwrite_pdf_with_searchable_version = schema.Bool(
        title=_(u'Overwrite PDF with searchable version'),
        description=_(u"Overwrite the original PDF with an OCR version created during the OCR process(must be used along with 'OCR Enabled' option). "
                      u"**only available if you have tesseract(version 3.0.1 or greater), pdftk and hocr2pdf(part of exactimage package) installed."),
        default=True
    )
    
    pdf_conversion_type = schema.Choice(
        title=u'PDF Conversion Type',
        description=u'When the ORC text is embedded into the pdf, a new PDF is created. Select a compression setting to use.',
        default=u'/screen',
        vocabulary=SimpleVocabulary([
            SimpleTerm('/screen', '/screen', u'Screen : low-resolution similar to Acrobat Distiller "Screen Optimized"'),
            SimpleTerm('/ebook', '/ebook', u'E-Book: medium-resolution similar to Acrobat Distiller "eBook"'),
            SimpleTerm('/printer', '/printer', u'Printer: similar to Acrobat Distiller "Print Optimized"'),
            SimpleTerm('/prepress', '/prepress', u'Pre-press: similar to Acrobat Distiller "Prepress Optimized"'),
            SimpleTerm('/default', '/default', u'Default: intended to be useful across a wide variety of uses - large file size.')
        ])
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

    