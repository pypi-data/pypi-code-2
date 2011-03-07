from Products.CMFCore.utils import getToolByName
from simplelayout.types.common.config import SIMPLE_LAYOUT_SIZES

from zope.component import queryUtility

from simplelayout.base.configlet.interfaces import ISimplelayoutConfiguration
from simplelayout.base.config import IMAGE_SIZE_MAP_PER_INTERFACE, \
                                     CONFIGLET_INTERFACE_MAP


class ImageScalesMixin(object):
    """Mixin class for configurable image scales support.
       get nfos from configlet
    """

    def getSlImageSizes(self):
        """
        """
        # default values
        image_sizes = {}
        conf = queryUtility(ISimplelayoutConfiguration, name='sl-config')
        if not conf.use_atct_scales:
            return SIMPLE_LAYOUT_SIZES

        for key in CONFIGLET_INTERFACE_MAP:
            conf = queryUtility(CONFIGLET_INTERFACE_MAP[key], name=key)
            if not conf:
                continue
            
            #read out all scales
            scales_raw = [IMAGE_SIZE_MAP_PER_INTERFACE[_d].values() for _d in IMAGE_SIZE_MAP_PER_INTERFACE]
            # create a one level list
            scales = []
            for l in scales_raw:
                scales += l
                
            for scale in scales:
                size = getattr(conf, scale, 0)
                if size != 0:
                    image_sizes[scale] = (size,10000)
            
        return image_sizes
