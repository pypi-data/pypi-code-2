from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from raptus.showcase.interfaces import IShowcaseImage, IShowcase

class ShowcaseView(BrowserView):
    """A view of a showcase object"""
    template = ViewPageTemplateFile('templates/showcase.pt')
   
    def __call__(self):
        return self.template()
      
    def showcasebox(self):
        
        if self.context.getShowcaseEditor():
            width, height = self.context.getShowcaseEditor().split(',')
        else:
            width, height = 510, 390
        
        showcasebox = {'style': '''width: %spx;
                                   height:%spx;
                                ''' % (width, height,),
                       'width': width,
                       'height': height,}
        
        return showcasebox
    
    @property
    def images(self):
        images = []
        catalog = getToolByName(self.context, 'portal_catalog')
        raw_images = catalog(object_provides=IShowcaseImage.__identifier__, path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1}, sort_on='getObjPositionInParent')
        for image in raw_images:
            image = image.getObject()
            
            reference = None
            reference_title = ''
            reference_description = ''
            if image.getReferenceField():
                reference = image.getReferenceField().absolute_url()
                reference_title = image.getReferenceField().Title
                reference_description = image.getReferenceField().Description
            
            images.append({'title': image.Title,
                           'url': image.absolute_url(),
                           'uid': image.UID,
                           'reference': reference,
                           'reference_title': reference_title,
                           'reference_description': reference_description,
                           'style': '''width:%spx;
                                       height:%spx;
                                       left:%spx;
                                       top:%spx;
                                       background-image:url(%s);
                                       ''' % (image.getWidth(),
                                              image.getHeight(),
                                              image.getClipLeft() or 0,
                                              image.getClipTop() or 0,
                                              image.absolute_url(),),
                           'wrapper': {'style': '''left: %spx;
                                                   top: %spx;
                                                   width: %spx;
                                                   height:% spx;
                                                   position: absolute;
                                                ''' % (image.getX() or 0,
                                                       image.getY() or 0,
                                                       image.getClipWidth() or image.getWidth(),
                                                       image.getClipHeight() or image.getHeight(),
                                                       ), },
                           'holder':   {'style': '''overflow: hidden;
                                                    position: absolute;
                                                    top: 0px;
                                                    right: 0px;
                                                    bottom: 0px;
                                                    left: 0px;
                                                 ''' },})
            
        images.reverse()  
        return images
   
class ShowcaseImageView(BrowserView):
    '''A view of a showcaseImage object'''
    template = ViewPageTemplateFile('templates/showcaseImage.pt')
   
    def __call__(self):
        return self.template()
    
    def title(self):
        return self.context.Title()
    
    def description(self):
        return self.context.Description()
    
    def image(self):
        image = {'url': self.context.absolute_url(),
                 'url_preview': '%s/image_preview' % self.context.absolute_url(),
                 'url_large':   '%s/image_large'   % self.context.absolute_url(),
                 'thumb':       '%s/image_thumb' % (self.context.absolute_url()),
                 'caption': self.context.Title(),
                 }
        
        return image
    
class ShowcaseFolder(object):
    template = ViewPageTemplateFile('templates/showcaseFolder.pt')
    
    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        self._brains_showcases = catalog(object_provides=IShowcase.__identifier__,
                                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                                      sort_on='getObjPositionInParent')
        return self.template()
    
    def navigation(self):
        raw_showcase = self._brains_showcases
        navigation = []
        number = self.selectedShowcaseNr()
        i = 0
        for showcase in raw_showcase:
            showcase = showcase.getObject()
            attributs =  ( {'title': showcase.Title(),
                            'url': '%s?number=%s'%(self.context.absolute_url(), i) })
            
            attr_class = ''
            if i == number:
                attr_class += 'selected '
            if i == number-1:
                attr_class += 'before_selected '
            if i == number+1:
                attr_class += 'after_selected '
            if i == 0:
                attr_class += 'first '
            if i == len(raw_showcase)-1:
                attr_class += 'last ' 
                
            attributs['class'] = attr_class
            
            navigation.append(attributs)
            i +=1
        return navigation
    
    def showcase(self):
        """ Return the VIEW from the selected showcase
        """
        
        index = self.selectedShowcaseNr()
        brains = self._brains_showcases

        if index < len(brains):
            return getMultiAdapter((brains[index].getObject(), self.request), name='view')
        else:
            return None
        
    def selectedShowcaseNr(self):
        raw_showcase = self._brains_showcases
        number = 0
        if self.context.REQUEST.has_key('number'):
            try:
                number = int(self.context.REQUEST.number)
            except:
                ''' the string is not a number :-/ '''
        if len(raw_showcase) <= number or 0 > number:
            number = 0
            
        return number
    
        
        