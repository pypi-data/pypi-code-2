from Products.ATContentTypes.interface import IATImage
from zope.component import adapter
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from unweb.watermark.extender import ImageExtender
from plone.app.blob.scale import BlobImageScaleHandler
from plone.app.imaging.traverse import DefaultImageScaleHandler
from PIL import Image, ImageEnhance
from cStringIO import StringIO
import urllib
import os
import tempfile
from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry 
from zope.component import getUtility

def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im
   
@adapter(IATImage, IActionSucceededEvent)
def imageFlow(obj, event):
    """ This gets called on workflow transitions. Whenever an image is published
        the original hires image is moved to the original image extended field 
        and a 768:768 watermarked image is set to the standard image field"""
   
    if event.action == 'publish':
        ImageExtender(obj).fields[0].set(obj, obj.getImage())
        applyWatermark(obj)
    elif event.action in ['reject','retract']:
        obj.setImage(ImageExtender(obj).fields[0].get(obj))

def applyWatermark(obj):
    """ Set the standard image field to hold a resized and watermarked copy of 
        the original image extended field """
    registry = getUtility(IRegistry)
    watermark = registry['unweb.watermark.interfaces.IWatermarkSettings.watermark_image']
    opacity = registry['unweb.watermark.interfaces.IWatermarkSettings.watermark_opacity']

    field = obj.getField('image')
    scaled = DefaultImageScaleHandler(field).getScale(obj, scale='large')
    f_image = StringIO(scaled.data)
    image = Image.open(f_image)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    # create a transparent layer the size of the 
    # image and draw the watermark in that layer.
    layer = Image.new('RGBA', image.size, (0,0,0,0))
    if watermark:
        mark = Image.open(StringIO(watermark))
        mark = reduce_opacity(mark, opacity)
        for y in range(0, image.size[1], mark.size[1]):
            for x in range(0, image.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
        image = Image.composite(layer, image, layer)
    f_data = StringIO()
    image.save(f_data, 'jpeg')
    obj.setImage(f_data.getvalue())
