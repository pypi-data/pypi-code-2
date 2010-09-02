from zope.i18nmessageid import MessageFactory
CDNMessageFactory = MessageFactory('sc.base.cdn')
import patch

patch.run()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
