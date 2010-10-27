from cStringIO import StringIO
from PIL import Image, ImageFilter
from PIL import ImageOps
from PIL.PngImagePlugin import PngImageFile
from PIL.ImageColor import getrgb

from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class ISharpenImage(Interface):
    """
   An Image View view interface
    """

    def test():
        """ test method"""

class SharpenImage(BrowserView):
    """ A browser view to be used on images 
    """    
    def __call__(self, REQUEST):
        img = self.context
        #img_data = str(obj.getField('image').getScale(obj, scale_name)) #ajungs suggestion, should work with PIL sizes
        img_data = getattr(img, '_data', False) or getattr(img, 'data', False) 
        image = Image.open(StringIO(img_data))
        
        newimage = image.filter(ImageFilter.SHARPEN)
        output = StringIO()
        newimage.save(output, format='PNG')
        self.request.response.setHeader('Content-Type','image/png')
        return output.getvalue()
             
                
class SquareImage(BrowserView):
    """ A browser view to be used on images 
    use ?position='xx" to place the image  (-xx for left / up )
    """    
    def __call__(self, REQUEST):
    	position = self.request.get('position', 'center')  #center image if not specified
        color = self.request.get('color', '#DDD')  #center image if not specified
        img = self.context
        img_data = getattr(img, '_data', False) or getattr(img, 'data', False) 
        image = Image.open(StringIO(img_data))
        
        #Calculate the size of the image
        fullWidth  = image.size[0] 
        fullHeight = image.size[1]
        
        if fullWidth >= fullHeight:
        	if position == 'center':
        	    positionx = (-(fullWidth-fullHeight)/2)
        	else:
        	    positionx = int(position)
 	    	fullWidth = fullHeight
 	    	positiony = 0
        else:
        	if position == 'center':
        	    positiony = (-(fullHeight-fullWidth)/2)
        	else:
        	    positiony = int(position)
 	    	fullHeight = fullWidth
 	    	positionx = 0
 
        
        #Create the squareimage
        squareimage = Image.new("RGB", (fullWidth, fullHeight), color ) 
        
        #Paste in the old image
        squareimage.paste(image, ( positionx , positiony ), )
        output = StringIO()
        squareimage.save(output, format='PNG')
        self.request.response.setHeader('Content-Type','image/png')
        return output.getvalue()