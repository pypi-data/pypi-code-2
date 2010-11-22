"""The product's interfaces"""
from zope import schema
from zope.interface import Interface

class IWatermarkSettings(Interface):
    """Watermark settings"""
    watermark_image = schema.Bytes(title = u'Watermark image file', 
                                   max_length = 1024 * 1024 * 50,
                                   )

    watermark_opacity = schema.Float(title = u'Watermark opacity percentage', 
                                     min = 0.1, 
                                     max = 1.0, 
                                     default = 0.15,
                                     )
