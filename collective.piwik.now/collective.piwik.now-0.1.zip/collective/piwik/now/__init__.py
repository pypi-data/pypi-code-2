from zope.i18nmessageid import MessageFactory
OnlineUsersMessageFactory = MessageFactory('collective.piwik.now')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
