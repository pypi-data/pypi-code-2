import logging

from django.template import Context, Template, loader
from django.core.exceptions import PermissionDenied

from error_pages.template import process_template, process_messages
from error_pages import config
from error_pages.http import *


class ErrorPageMiddleware(object):
    def __init__(self):
        self.template = self.code = self.exception = None

    def process_exception(self, request, exception):
        '''Process exceptions raised in view code'''
        self.exception = exception

        for i in globals():
            if i.startswith('Http'):
                http_match = isinstance(exception, globals()[i])
                perm_deny = isinstance(exception, PermissionDenied)
                if http_match or perm_deny:
                    if http_match:
                        self.code = int(i[-3:])
                    elif perm_deny:
                        self.code = 403

                    self.template = '%d.html' % self.code
                    break

    def process_response(self, request, response):
        '''Process the response by status code'''
        # no exception raised by user, but it could still be error page worthy
        if not self.code:
            if response.status_code in [400, 401, 402, 403, 404, 405, 406, 407, 408,
                                        409, 410, 411, 412, 413, 414, 415, 416, 417,
                                        418, 422, 423, 424, 425, 426,
                                        500, 501, 502, 503, 504, 505, 507, 509, 510]:
                self.code = response.status_code
                self.template = '%d.html' % response.status_code

        # let django handle these codes instead
        if self.code in [404, 500]:
            self.template = self.code = None

        # ok, now log a warning
        if config.DEBUG and self.code:
            # but skip the warning if we have a login form.
            # it is the users job to implement a warning
            # after processing their login
            try:
                if self.exception.site is None:
                    raise ValueError
            except:
                title = process_messages(self.code)[0]
                t = []
                for word in title.split(' '):
                    t.append(word.capitalize())
                logging.warning('%s: %s' % (' '.join(t), request.path),
                                extra={
                                    'status_code': self.code,
                                    'request': request
                                })

        if self.template is not None:
            # dont alter the response if we don't want the error page rendered
            if config.ERRORPAGES_PAGES_ENABLED and self.code not in config.ERRORPAGES_PAGES_IGNORE:
                if config.DEBUG:
                    TEMPLATE = process_template(self.code)
                    t = Template(TEMPLATE, name='Error Page Template')
                else:
                    t = loader.get_template(self.template)

                response = HttpResponse(t.render(Context({'request': request})), status=self.code)

        # bring up login form if user wants one
        if self.code == 401:
            try:
                if self.exception.site:
                    response['WWW-Authenticate'] = 'Basic realm="%s"' % self.exception.site
            except:
                pass

        return response
