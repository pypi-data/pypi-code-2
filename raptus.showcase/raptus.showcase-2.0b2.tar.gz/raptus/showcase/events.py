from Products.CMFCore.utils import getToolByName
from raptus.showcase.interfaces import IShowcaseImage

def showcaseEditEvent(obj, event):
    """ set the propertis for the images...
    """
    req = obj.REQUEST

    catalog = getToolByName(obj, 'portal_catalog')
    raw_images = catalog(object_provides=IShowcaseImage.__identifier__,
                         path={'query': '/'.join(obj.getPhysicalPath()),
                               'depth': 1
                               },
                         sort_on='getObjPositionInParent')
    if req.has_key('img'):
        for newImg in req.img:
            for rawImg in raw_images:
                rawImg = rawImg.getObject();
                if rawImg.UID() == newImg['uid']:
                    rawImg.setX(newImg['x'][:-2])
                    rawImg.setY(newImg['y'][:-2])
                    rawImg.setClipWidth(newImg['width'][:-2])
                    rawImg.setClipHeight(newImg['height'][:-2])
                    rawImg.setClipLeft(newImg['clipLeft'][:-2])
                    rawImg.setClipTop(newImg['clipTop'][:-2])
                    
                    obj.moveObjectToPosition(rawImg.getId(), len(raw_images)-int(newImg['zindex']))

                rawImg.reindexObject()
    
    obj.setShowcaseEditor(req.showcaseWidth+','+req.showcaseHeight)

    