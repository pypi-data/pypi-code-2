"""
Django-partial-page is a middleware that allows your views send the whole pages as usual or just parts of the same pages.

Add the middleware to settings.MIDDLEWARE_CLASSES. For it to work,
1. The process_views of the middleware above should not short-circuit by calling the view prematurely.
2. The middleware below should not substitute the TemplateResponse with something else.

If other middleware changes directly response.content, these changes will be ignored.
"""
