from zope.interface import Interface, implements
from zope.configuration.fields import GlobalObject
from zope.component.zcml import IAdapterDirective, adapter as add_adapter
from collective.plonetruegallery.interfaces import IGallery
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from collective.plonetruegallery.interfaces import IGalleryAdapter, IDisplayType, IBaseSettings
from collective.plonetruegallery.config import named_adapter_prefix
from collective.plonetruegallery.settings import GallerySettings

GalleryTypes = []
DisplayTypes = []

def getAllGalleryTypes():
    return GalleryTypes
    
def getAllDisplayTypes():
    return DisplayTypes

def getDisplayType(name):
    for t in DisplayTypes:
        if t.name == name:
            return t
            
    return None

class IBaseTypeDirective(Interface):
    condition = GlobalObject(
        title=u"Condition Method",
        description=u"Method that returns a boolean to check whether or not the adapter should be used",
        required=False
    )

class IGalleryTypeDirective(IAdapterDirective, IBaseTypeDirective):
    """
    """

    
class IDisplayTypeDirective(IAdapterDirective, IBaseTypeDirective):
    """
    pretty much just a browser page... just have to do some extra work...
    """

def create_settings_factory(schema):
    class Settings(GallerySettings):
        implements(schema)
        
        def __init__(self, context, interfaces=[schema]):
            super(Settings, self).__init__(context, interfaces)
            
    return [Settings]

def add_gallery_type(_context, factory, provides=IGalleryAdapter, for_=[IGallery, IDefaultBrowserLayer], 
                    permission=None, name='', trusted=False, locate=False, condition=None):

    gallerytype = factory[0]
    if condition is not None and not condition():
        return
    
    if len(factory) != 1:
        raise Exception("Can only specify one factory")
    
    if not IGalleryAdapter.implementedBy(gallerytype):
        raise Exception(
            "%s gallery adapter must implement IGalleryAdapter" % gallerytype.name
        )
    
    if not gallerytype.schema.isOrExtends(IBaseSettings):
        raise Exception(
            "%s gallery adapter must have settings attribute "
            "of implemented settings" % gallerytype.name
        )
    
    GalleryTypes.append(gallerytype)
    add_adapter(_context, factory, provides, for_, permission, 
        named_adapter_prefix + gallerytype.name, trusted, locate)
    
    # also add an un-named adapter to handle form edits of this data via z3c.forms...
    add_adapter(_context, create_settings_factory(gallerytype.schema), 
        provides=gallerytype.schema, for_=[IGallery])
    
def add_display_type(_context, factory, provides=IDisplayType, for_=[IGalleryAdapter], 
                    permission=None, name='', trusted=False, locate=False, condition=None):

    displaytype = factory[0]
    if condition is not None and not condition():
        return

    if not IDisplayType.implementedBy(displaytype):
        raise Exception("%s display type must implement IDisplayType" % displaytype.name)
        
    if not displaytype.schema.isOrExtends(IBaseSettings):
        raise Exception("%s display type must have settings "
                        "attribute of implemented settings" % displaytype.name)

    DisplayTypes.append(displaytype)

    add_adapter(_context, factory, provides, for_, permission, 
        named_adapter_prefix + displaytype.name, trusted, locate)
    
    # also add an un-named adapter to handle form edits of this data via z3c.forms...
    add_adapter(_context, create_settings_factory(displaytype.schema), 
        provides=displaytype.schema, for_=[IGallery])
