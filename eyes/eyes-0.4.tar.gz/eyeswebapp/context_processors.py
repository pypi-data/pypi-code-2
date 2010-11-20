""" common template enhancing context processors.

A context processor is a method that takes an HTTP request object and returns a 
dictionary. The dictionaries of all processors defined in settings
(TEMPLATE_CONTEXT_PROCESSORS) get merged together and used for template
processing.
"""
from django.conf import settings

def common(request):
    """ This is a project specific context processor that injects various
    interesting values into the Context object, for use by our templates."""
        
    ctx = {}
    ctx['MEDIA_URL'] = settings.MEDIA_URL

    return ctx
