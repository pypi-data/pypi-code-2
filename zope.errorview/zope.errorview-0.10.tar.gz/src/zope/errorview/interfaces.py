from zope.interface import Interface, implements, Attribute

class IHandleExceptionEvent(Interface):
    """Event fired when handling an exception."""

    request = Attribute('The current request')

class HandleExceptionEvent(object):
    implements(IHandleExceptionEvent)

    def __init__(self, request):
        self.request = request
