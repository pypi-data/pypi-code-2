from cStringIO import StringIO
from hexagonit import swfheader

from zope import interface, component

from Products.CMFCore.utils import getToolByName

from raptus.article.core.interfaces import IArticle
from raptus.article.flash.interfaces import IFlashs, IFlash, IFlashSize

class Flashs(object):
    """ Provider for flash movies contained in an article
    """
    interface.implements(IFlashs)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getFlashs(self, **kwargs):
        """ Returns a list of flash movies (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Flash', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                  'depth': 1}, sort_on='getObjPositionInParent', **kwargs)

class FlashSize(object):
    """ Handler for image thumbing and captioning
    """
    interface.implements(IFlashSize)
    component.adapts(IFlash)
    
    def __init__(self, context):
        self.context = context
        
    def getSize(self, size="original"):
        """
        Returns the width and height registered for the specific size
        
        The sizes are taken from the raptus_article properties sheet
        and are formed by the following name schema:
        
            flash_<size>_(height|width)
        """
        metadata = swfheader.parse(StringIO(str(self.context.getFile().data)))
        w, h = float(metadata['width']), float(metadata['height'])
        props = getToolByName(self.context, 'portal_properties').raptus_article
        tw, th = float(props.getProperty('flash_%s_width' % size, 0)), float(props.getProperty('flash_%s_height' % size, 0))
        if tw and tw < w:
            h = tw / w * h
            w = tw
        if th and th < h:
            w = th / h * w
            h = th
        return int(w), int(h)
        
