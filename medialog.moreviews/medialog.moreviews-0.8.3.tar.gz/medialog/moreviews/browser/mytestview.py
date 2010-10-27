from cStringIO import StringIO
from PIL import Image, ImageFilter
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFont
from PIL.PngImagePlugin import PngImageFile
from PIL.ImageColor import getrgb

from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class IMyTestView(Interface):
    """
    An Image View view interface
    """

    def test():
        """ test method"""

class MyTestView(BrowserView):
    """ A browser view to be used on images 
    """    
    def __call__(self, REQUEST):
        color = self.request.get('color', '#704214')  #Using sepia if no color is specified
        img = self.context
        #img_data = str(obj.getField('image').getScale(obj, scale_name)) #ajungs suggestion, should work with PIL sizes
        img_data = getattr(img, '_data', False) or getattr(img, 'data', False) 
        image = Image.open(StringIO(img_data))
        
        draw = ImageDraw.Draw ( image )
        draw.text ( (10,10), "Run awayyyy!",)
        output = StringIO()
        image.save(output, format='PNG')
        self.request.response.setHeader('Content-Type','image/png')
        return output.getvalue()
        
        

        
