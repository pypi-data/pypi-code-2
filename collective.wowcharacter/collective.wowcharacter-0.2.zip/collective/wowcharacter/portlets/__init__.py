from zope.i18nmessageid import MessageFactory
ExamplePortletMessageFactory = MessageFactory('collective.wowcharacter.realmstatus')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
