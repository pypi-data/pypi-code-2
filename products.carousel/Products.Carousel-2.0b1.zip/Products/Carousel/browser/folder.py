from persistent import Persistent
import ExtensionClass
from zope.annotation import factory
from zope.component import adapts
from zope.interface import implements
from z3c.form import form, field, group
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget, \
    CheckBoxFieldWidget
from plone.app.z3cform.layout import FormWrapper
from Products.CMFCore.interfaces import IFolderish
from Products.ATContentTypes.interface.topic import IATTopic
from Products.Carousel.interfaces import ICarousel, ICarouselSettings, \
    ICarouselFolder, ICarouselSettingsView, ICarouselBanner
from Products.Carousel import CarouselMessageFactory as _

class Carousel(ExtensionClass.Base):
    implements(ICarousel)
    adapts(ICarouselFolder)
    
    def __init__(self, context):
        self.context = context
        
    def getSettings(self):
        """
        Returns an object that provides ICarouselSettings.
        """
        
        return ICarouselSettings(self.context)

    def getBanners(self):
        """
        Returns a list of objects that provide ICarouselBanner.
        """
        
        banner_objects = []
        if IFolderish.providedBy(self.context):
            banner_objects = self.context.objectValues()
        elif IATTopic.providedBy(self.context):
            banner_objects = [brain.getObject() for brain \
                in self.context.queryCatalog()]
        
        return [b for b in banner_objects if ICarouselBanner.providedBy(b)]

class CarouselSettings(Persistent):
    """
    Settings for a Carousel instance.
    """
    
    implements(ICarouselSettings)
    adapts(ICarouselFolder)
    
    def __init__(self):
        self.enabled = True
        self.banner_template = u'@@banner-default'
        self.banner_elements = [u'title', u'text', u'image']
        self.width = None
        self.height = None
        self.pager_template = u'@@pager-numbers'
        self.transition_type = u'fade'
        self.transition_speed = 0.5
        self.transition_delay = 8.0
        self.default_page_only = True
        
CarouselSettingsFactory = factory(CarouselSettings)

class AppearanceGroup(group.Group):
    """
    Appearance options.
    """

    label = _(u'Appearance')
    fields = field.Fields(ICarouselSettings).select(
        'banner_template', 'banner_elements', 'width', 'height',
        'pager_template')
    fields['banner_elements'].widgetFactory = CheckBoxFieldWidget

class TransitionGroup(group.Group):
    """
    Transition options.
    """

    label = _(u'Transition')
    fields = field.Fields(ICarouselSettings).select(
        'transition_type', 'transition_speed', 'transition_delay')

class DisplayGroup(group.Group):
    """
    Display options.
    """

    label = _(u'Display')
    fields = field.Fields(ICarouselSettings).select(
        'enabled', 'default_page_only')
    fields['enabled'].widgetFactory = SingleCheckBoxFieldWidget
    fields['default_page_only'].widgetFactory = SingleCheckBoxFieldWidget

class CarouselSettingsForm(group.GroupForm, form.EditForm):
    """
    Form for editing Carousel settings.
    """
    
    label = _(u'Carousel Settings')
    description = _(u'Carousel allows you to create a rotating display of' 
        ' banners that contain images and text. To add a banner, use the'
        ' Add New menu above. To modify existing banners, click the'
        ' Contents tab.')
    groups = (AppearanceGroup, TransitionGroup, DisplayGroup,)
    
    def getContent(self):
        return ICarouselSettings(self.context)
        
CarouselSettingsForm.buttons['apply'].title = _(u'Save')
        
class CarouselSettingsView(FormWrapper):
    """
    View for searching and filtering ATResources.
    """
    
    implements(ICarouselSettingsView)

    form = CarouselSettingsForm    