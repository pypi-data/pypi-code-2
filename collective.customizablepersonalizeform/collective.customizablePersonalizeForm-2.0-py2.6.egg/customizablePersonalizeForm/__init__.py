from zope.i18nmessageid import MessageFactory

CollectiveCustomizablePFMessageFactory = MessageFactory('collective.customizablePersonalizeForm')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
