from django.conf import settings
from django.core.urlresolvers import get_callable

if 'jqtouch' in settings.INSTALLED_APPS:
    if not hasattr(settings,'JQTOUCH_BASE_IDENTIFIER'):
        settings.JQTOUCH_BASE_IDENTIFIER = 'default'
    
    if not hasattr(settings, 'JQTOUCH_PANEL_RESOLVERS'):
        settings.JQTOUCH_PANEL_RESOLVERS = ('jqtouch.resolvers.panel_model_resolver',)
    
    if isinstance(settings.JQTOUCH_PANEL_RESOLVERS, basestring) or callable(settings.JQTOUCH_PANEL_RESOLVERS):
        settings.JQTOUCH_PANEL_RESOLVERS = (settings.JQTOUCH_PANEL_RESOLVERS,)
    
    if not isinstance(settings.JQTOUCH_PANEL_RESOLVERS, (tuple,list,)):
        raise ValueError('JQTOUCH_PANEL_RESOLVERS must be a list or tuple')
    
    settings.JQTOUCH_PANEL_RESOLVERS = map(get_callable,
                                           settings.JQTOUCH_PANEL_RESOLVERS)
    
    for resolver in settings.JQTOUCH_PANEL_RESOLVERS:
        if isinstance(resolver, basestring):
            raise ValueError('%s could not be resolved to a callable' % (resolver,))
