from zope.i18nmessageid import MessageFactory
easyslider_message_factory = MessageFactory('collective.easyslider')

from settings import PageSliderSettings, ViewSliderSettings
from interfaces import ISliderLayer, ISliderPage, IViewEasySlider, ISliderUtilProtected, \
                       ISliderUtil, ISliderSettings, IPageSliderSettings, IViewSliderSettings, \
                       ISlide, ISlidesContext, ISlideContext

import logging
logger = logging.getLogger('collective.easyslider')

try:
    from collective.easytemplate.engine import getEngine 
    from tags import SliderTag
    engine = getEngine()
    engine.addTag(SliderTag())
    logger.info("Installed slider easytemplate tag")
except:
    logger.info("easytemplate not installed. Can not install slider tag") 

def initialize(context):
    pass
