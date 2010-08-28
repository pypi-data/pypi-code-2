from zope.interface import Interface, Attribute
from zope import schema
from collective.easyslider import easyslider_message_factory as _
from zope.schema.vocabulary import SimpleVocabulary
from OFS.interfaces import IItem

class ISliderLayer(Interface):
    """
    marker interface for slider layer
    """

class ISliderPage(Interface):
    """
    marker interface for a page that implements
    the Slider 
    """

class IViewEasySlider(Interface):
    """
    marker interface for content types that can use
    easyslider view
    """

class ISliderUtilProtected(Interface):
    
    def enable():
        """
        enable slider on this object
        """
    
    def disable():
        """
        disable slider on this object
        """
        
class ISliderUtil(Interface):
    
    def enabled():
        """
        checks if slider is enabled on the peice of content
        """
        
    def view_enabled():
        """
        checks if the slider view is selected
        """
    def should_include():
        """
        if the slider files should be included
        """
    
class ISliderSettings(Interface):
    """
    The actual slider settings
    """
    
    width = schema.Int(
        title=_(u'label_width_title_slider_setting', default=u"Width"),
        description=_(u"label_width_description_slider_setting", 
            default=u"The fixed width of the slider."),
        default=600,
        required=True
    )
    
    height = schema.Int(
        title=_(u'label_height_title_slider_setting', default=u"Height"),
        description=_(u"label_height_description_slider_setting", 
            default=u"The fixed height of the slider."),
        default=230,
        required=True
    )
    
    show = schema.Bool(
        title=_(u"label_show_title_slider_setting", default=u"Show it?"),
        description=_(u"label_show_description_slider_setting",
            default=u"Do you want the easy slider to show on this page?"),
        default=True,
        required=True
    )
    
    effect = schema.Choice(
        title=_(u"label_effect_title_slider_setting", default=u"Effect Type"),
        description=_(u"label_effect_description_slider_setting",
            default=_(u"I know the product is called easySLIDER, but we "
                      u"decided to let you choose multiple effects now")),
        default="Slide",
        vocabulary=SimpleVocabulary.fromValues([
            'Slide',
            'Fade'
        ])
    )

    vertical = schema.Bool(
        title=_(u"label_vertical_title_slider_setting", default=u"Vertical?"),
        description=_(u"label_vertical_description_slider_setting", 
            default=u"Should the slide transition vertically?"),
        default=False
    )
    
    speed = schema.Int(
        title=_(u"label_speed_title_slider_setting", default=u"Speed"),
        description=_(u"label_speed_description_slider_setting",
            default=u"Speed at which the slide will transition."),
        default=800
    )
    
    auto = schema.Bool(
        title=_(u"label_auto_title_slider_setting", default=u"Auto?"),
        description=_(u"label_auto_description_slider_setting",
            default=u"Should the slider automatically transition?"),
        default=True
    )
    
    pause = schema.Int(
        title=_(u"label_pause_title_slider_setting", default=u"Pause"),
        description=_(u"label_pause_description_slider_setting",
            default=u"How long the slide should pause before it is automatically transitioned."),
        default=4000
    )
    
    continuous = schema.Bool(
        title=_(u"label_continuous_title_slider_setting", default=u"Continuous?"),
        description=_(u"label_continuous_description_slider_setting",
            default=u"Should the slider continuously loop?"),
        default=True
    )
    
    centered = schema.Bool(
        title=_(u"label_centered_title_slider_setting", default=u"Centered?"),
        description=_(u"label_centered_description_slider_setting",
            default=u"Should the easyslider be centered?"),
        default=True
    )
    
    navigation_type = schema.Choice(
        title=_(u"label_navigation_type_title_slider_setting", default=u"Type of Navigation."),
        description=_(u"label_navigation_type_description_slider_setting",
            u"Choose the type of navigation to use."),
        default="Navigation Buttons",
        vocabulary=SimpleVocabulary.fromValues([
            'Big Arrows',
            'Small Arrows',
            'Navigation Buttons',
            'No Buttons'
        ])
    )
    
    fade_navigation = schema.Bool(
        title=_(u"label_fade_navigation_title_slider_settings", default=u"Fade Navigation?"),
        description=_(u"label_fade_navigation_description_slider_settings",
            default=u"Should the navigation fade in and out when a user hovers of the slider?"),
        default=False
    )
    
class IPageSliderSettings(ISliderSettings):
    """
    difference here is the user creates all his slides
    """
    
    slides = schema.List(
        title=_(u"label_slides_title_slider_setting", default=u"Slides"),
        description=_(u"label_slides_description_slider_settings",
            default=u"These are the slides that will show up in the easySlider for this page."),
        default=[]
    )
    
class IViewSliderSettings(ISliderSettings):
    """
    settings for the slider view on a collection or folder
    """
    
    allowed_types = schema.Tuple(
        title=_(u"label_allowed_types_title_slider_setting", default=u'Availble Slide Types'),
        description=_(u"label_allowed_types_description_slider_setting", 
            default=u"Select the types that will be show in this slider."),
        required=True,
        missing_value=None,
        default=("News Item", "Image"),
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary.fromValues([
                'Image',
                'News Item'
            ])
        )
    )
    
    limit = schema.Int(
        title=_(u"label_limit_title_slider_setting", default=u"Max Slides"),
        description=_(u"label_limit_description_slider_setting", 
            default=u"The max amount of content items to use for slides.  Set to 0 for unlimited."),
        default=0
    )
    
class ISlide(Interface):
    
    slide = schema.Text(
        title=_(u"label_slide_title_slider_setting", default=u"Slide")
    )
    index = schema.Int(
        title=u'',
        required=False
    )
    
class ISlidesContext(IItem):
    """
    Context to allow traversing to the slides list
    """
    
class ISlideContext(IItem):
    """
    Context to allow traversing to a slide on a ISlidesContext object
    """
    index = Attribute("""Index of the slide on the object""")
    