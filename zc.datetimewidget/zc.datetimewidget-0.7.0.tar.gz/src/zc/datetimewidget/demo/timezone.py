import pytz
from zope import interface, component
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.browser import IBrowserRequest

TZINFO=pytz.timezone('Europe/Vienna')

@interface.implementer(ITZInfo)
@component.adapter(IBrowserRequest)
def tzinfo(request):

    """This adapter adapts any interface to the timezone where this
    demo was written.

    >>> print tzinfo(None)
    Europe/Vienna
    """
    return TZINFO


