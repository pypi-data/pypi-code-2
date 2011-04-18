from meta.zcml import GalleryTypes, DisplayTypes
from zope.component import getMultiAdapter, getAdapter
from settings import GallerySettings
from interfaces import IGallerySettings
from collective.plonetruegallery.config import named_adapter_prefix
from vocabularies import GalleryTypeVocabulary, DisplayTypeVocabulary
    
def getGalleryAdapter(gallery, request, gallery_type=None):
    if gallery_type is None:
        gallery_type = GallerySettings(gallery).gallery_type
    
    possible_types = GalleryTypeVocabulary(gallery)
    if gallery_type not in possible_types.by_value.keys():
        gallery_type = IGallerySettings['gallery_type'].default
    
    return getMultiAdapter(
        (gallery, request), 
        name=named_adapter_prefix + gallery_type
    )
            
def getDisplayAdapter(adapter, display_type=None):
    if display_type is None:
        display_type = GallerySettings(adapter.gallery).display_type
        
    possible_types = DisplayTypeVocabulary(adapter.gallery)
    if display_type not in possible_types.by_value.keys():
        display_type = IGallerySettings['display_type'].default
        
    return getAdapter(
        adapter, 
        name=named_adapter_prefix + display_type
    )
