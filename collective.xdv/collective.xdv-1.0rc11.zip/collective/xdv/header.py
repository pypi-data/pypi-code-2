from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from collective.xdv.utils import getHost
from collective.xdv.interfaces import ITransformSettings

def setHeader(object, event):
    """Set a header X-XDV in the request if XDV is enabled.

    This is useful for checking in things like the portal_css/portal_javascripts
    registries.
    """
    
    request = event.request
    
    registry = queryUtility(IRegistry)
    if registry is None:
        return
    
    settings = None
    try:
        settings = registry.forInterface(ITransformSettings)
    except KeyError:
        return
    
    if not settings.enabled:
        return
    
    domains = settings.domains
    if not domains:
        return
    
    host = getHost(request)
    for domain in domains:
        if domain.lower() == host:
            request.environ['HTTP_X_XDV'] = True
            return
