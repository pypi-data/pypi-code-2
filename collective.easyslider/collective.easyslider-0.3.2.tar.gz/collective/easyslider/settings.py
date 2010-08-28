from zope.interface import implements
from persistent.dict import PersistentDict
try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations

from interfaces import IPageSliderSettings, IViewSliderSettings, ISliderSettings

class SliderSettings(object):
    """
    Pretty much copied how it is done in Slideshow Folder
    hopefully no one is foolish enough to want a custom slider
    and a view slider.  If they are then the settings will 
    overlap.  
    """
    implements(IPageSliderSettings)
    
    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)

        self._metadata = annotations.get('collective.easyslider', None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations['collective.easyslider'] = self._metadata
                    
    def __setattr__(self, name, value):
        if name[0] == '_' or name == 'context':
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

class PageSliderSettings(SliderSettings):
    def __getattr__(self, name):
        if name == 'slides':
            # somehow this default value gets manually set. This prevents this
            # form happening on the slides...
            return self._metadata.get(name, [])
            
        return self._metadata.get(name, IPageSliderSettings[name].default)
        
class ViewSliderSettings(SliderSettings):
    def __getattr__(self, name):
        return self._metadata.get(name, IViewSliderSettings[name].default)
        