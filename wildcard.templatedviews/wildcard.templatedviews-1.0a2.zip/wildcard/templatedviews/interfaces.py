from zope.interface import Interface, Attribute
from zope import schema
from wildcard.templatedviews.vocabularies import SettingsContextSourceBinder

class IBaseSettings(Interface):
    pass

class ITemplated(Interface):
    settings = Attribute("An inteface that defines the settings for this template.")
    
    
class ITemplatedSettings(Interface):
    
    template_name = schema.Choice(
        title=u'Template',
        required=True,
        vocabulary="wildcard.templatedviews.templates"
    )
    
class ILayer(Interface):
    pass
    
class ITemplatedView(Interface):
    def enabled():
        pass
        
        
class IReferencedTemplate(Interface):
    reference = schema.Choice(
        title=u'Referenced item',
        description=u'Select an item you would like to use the template of',
        required=True,
        source=SettingsContextSourceBinder({}, default_query='path:')
    )