from collective.amberjack.core.interfaces import IAmberjackSkin
from zope.interface import implements


class SafariSkin(object):
    implements(IAmberjackSkin)
    title = u"Safari"

class ModelTSkin(object):
    implements(IAmberjackSkin)
    title = "Model_t"

class LightGreySkin(object):
    implements(IAmberjackSkin)
    title = "Light Grey"
    
class SunburstSkin(object):
    implements(IAmberjackSkin)
    title = "Sunburst"