from zope.i18nmessageid import MessageFactory
ContentProviderPortletMessageFactory = MessageFactory('collective.portlet.contentprovider')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
