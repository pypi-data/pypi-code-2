from zope.i18nmessageid import MessageFactory
easyslider_message_factory = MessageFactory('collective.easyslider')

from settings import PageSliderSettings, ViewSliderSettings
from interfaces import ISliderLayer, ISliderPage, IViewEasySlider, ISliderUtilProtected, \
                       ISliderUtil, ISliderSettings, IPageSliderSettings, IViewSliderSettings, \
                       ISlide, ISlidesContext, ISlideContext

