from zope.interface import implements
from Products.RichImage.interfaces import ICropModifiedEvent
from zope.component.interfaces import ObjectEvent

class CropModifiedEvent(ObjectEvent):
    implements(ICropModifiedEvent)

    def __init__(self, fieldname, imageid, object, image):
        self.fieldname = fieldname
        self.imageid = imageid
        self.object = object
        self.image = image

def translateCrop(obj, event):
    """Use the same crop across translations"""
    field = obj.getField(event.fieldname)
    if field.languageIndependent:
        translations = obj.getTranslations()
        for t,_ in translations.values():
            if t is not obj:
                # Probably using annotation storage
                field.getStorage(obj).set(event.imageid, 
                                          t, 
                                          event.image, 
                                          mimetype=event.image.content_type, 
                                          filename=event.image.filename)
