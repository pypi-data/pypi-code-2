from cStringIO import StringIO
from PIL import Image, ImageFilter
from PIL import ImageOps
from PIL.PngImagePlugin import PngImageFile
from PIL.ImageColor import getrgb

from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class IDropShadowImage(Interface):
    """
    Drop Shadow Image View interface
    """

    def test():
        """ test method"""

class DropShadowImage(BrowserView):
    """ A browser view to be used wit images to get a drop shadow effect """    
    def __call__(self):
        img = self.context
        img_data = getattr(img, '_data', False) or getattr(img, 'data', False)
        image = Image.open(StringIO(img_data))
        border = 3
        backgroundColour = 'white'
        shadowColour = '#999999'
        offset = 6 # offset for the drop shadow
        iterations = 4

        #Calculate the size of the shadow-image
        fullWidth  = image.size[0] + abs(offset) + 2*border
        fullHeight = image.size[1] + abs(offset) + 2*border
 
        #Create the shadow's image. Match the parent image's mode.
        #should read image mode from image.mode, but for some reason this doesnt work
        shadow = Image.new("RGB", (fullWidth, fullHeight), backgroundColour) 
        
        # Place the shadow, with offset
        shadowLeft = border + max(offset, 0) #if <0, push the rest of the image right
        shadowTop  = border + max(offset, 0) #if <0, push the rest of the image down
        #Paste in the constant colour
        shadow.paste(shadowColour, 
                [shadowLeft, shadowTop,
                 shadowLeft + image.size[0],
                 shadowTop  + image.size[1] ])
 
        # Apply the BLUR filter repeatedly
        for i in range(iterations):
            shadow = shadow.filter(ImageFilter.BLUR)
 
        # Paste the original image on top of the  drop shadow 
        imgLeft = border - min(offset, 0) #if the shadow offset was < 0, push right
        imgTop  = border - min(offset, 0) #if the shadow offset was < 0, push down
        shadow.paste(image, (imgLeft, imgTop))
        output = StringIO()
        shadow.save(output, format='PNG')
        self.request.response.setHeader('Content-Type','image/png')
        return output.getvalue()
        
