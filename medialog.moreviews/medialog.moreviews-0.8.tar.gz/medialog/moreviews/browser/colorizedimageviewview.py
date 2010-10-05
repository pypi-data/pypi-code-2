from cStringIO import StringIO
from PIL import Image
from PIL import ImageOps
from PIL.PngImagePlugin import PngImageFile
from PIL.ImageColor import getrgb

from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class IColorizedImage(Interface):
    """
    Colorized Image View view interface
    """

    def test():
        """ test method"""

class ColorizedImage(BrowserView):
    """ A browser view to be used on images 
    Use it like this: path/to/image/colorizedimage?color=%23123456 or
                      path/toimage//colorizedimage?color=red """    
    def __call__(self, REQUEST):
        color = self.request.get('color', '#704214')  #Using sepia if no color is specified
        print color
        img = self.context
        img_data = getattr(img, '_data', False) or getattr(img, 'data', False)
        image = Image.open(StringIO(img_data))
        alpha = None
        if image.mode == 'RGBA':
            alpha = image.split()[3]
        elif image.mode == 'P' and image.format == 'PNG':
            # PNG images can have transparency and be palette-based.
            # This is probably not the most clever method but it works
            alpha = image.convert('RGBA').split()[3]
        r,g,b = getrgb(color)
        if image.mode != 'L':
            grayscale_image = image.convert('L')
        else:
            grayscale_image = image
        newimage = ImageOps.colorize(grayscale_image, (r,g,b),(255,255,255))
        output = StringIO()
        if alpha:
            newimage.putalpha(alpha)
        newimage.save(output, format='PNG')
        self.request.response.setHeader('Content-Type','image/png')
        return output.getvalue()