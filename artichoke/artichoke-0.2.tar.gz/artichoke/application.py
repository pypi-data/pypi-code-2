from webob import Request, Response
from webob.exc import HTTPFound
from authenticator import CookieAuthenticator

from mail_traceback import send_traceback, format_traceback
import traceback, mimetypes, os

class ArtichokeHelpers(object):
    pass

class Application(object):
    def __init__(self, root, templates_path, config={}):
        self.root = root(self, templates_path, config.get('helpers', ArtichokeHelpers()))
        self.statics = config.get('statics', 'public')
        self.autoreload_templates = config.get('autoreload', False)

        requested_authenticator = config.get('authenticator')
        if not requested_authenticator:
            self.authenticator = CookieAuthenticator()
        else:
            self.authenticator = requested_authenticator()

        self.mail_errors_to = config.get('mail_errors_to')
        self.mail_errors_from = config.get('mail_errors_from', 'artichoke@localhost')
        self.traceback = config.get('traceback', True)

    def __call__(self, environ, start_response):
        request = Request(environ=environ)

        static_path = self.statics + request.path_info
        if os.path.exists(static_path) and os.path.isfile(static_path):
            response = Response(body=open(static_path).read(), status=200,
                                headerlist=[('Content-type', mimetypes.guess_type(static_path)[0])])
        else:
            try:
                self.authenticator.authenticate(request)
                response = self.root._dispatch(request)
                self.authenticator.inject_cookie(response)
            except HTTPFound, e:
                response = e
                self.authenticator.inject_cookie(response)
            except Exception, e:
                if self.mail_errors_to:
                    mail_traceback(self.mail_errors_from, self.mail_errors_to)

                if self.traceback:
                    format_error_body = traceback.format_exc()
                    try:
                        format_error_body = format_traceback()
                        format_content_type = 'text/html'
                    except:
                        format_content_type = 'text/plain'
                    response = Response(body=format_error_body, status=500,
                                        headerlist=[('Content-type', format_content_type)])
                else:
                    response = Response(body="Internal Server Error", status=500,
                                        headerlist=[('Content-type', 'text/html')])
        return response(environ, start_response)
