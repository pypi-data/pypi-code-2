from zope import interface
from zope.component.interfaces import ObjectEvent, IObjectEvent

class IUploadFileView(interface.Interface):

    """a file upload view"""

class IFlashUploadForm(interface.Interface):

    """Form containing the swf for upload movie"""
    
class IFlashUploadedEvent(IObjectEvent):
    """ Event gets fired when flash uploaded an item """
    
class FlashUploadedEvent(ObjectEvent):
    interface.implements(IFlashUploadedEvent)
    
 