import webob

# TODO: would be nice to make middleware smarter so it could work with
# a streamed HTML body instead of serializing it out to body. That
# would complicate the middleware signicantly, however. We would for
# instance need to recalculate content_length ourselves.

class Middleware(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        req = webob.Request(environ)
        res = req.get_response(self.application)
        if not res.content_type.lower() in ['text/html', 'text/xml']:
            return res(environ, start_response)
        needed = environ.get('hurry.resource.needed', None)
        if needed is None:
            return res(environ, start_response)
        res.body = needed.render_topbottom_into_html(res.body)
        return res(environ, start_response)
