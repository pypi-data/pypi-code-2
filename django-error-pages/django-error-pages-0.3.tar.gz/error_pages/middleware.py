import logging

from django.template import Context, Template, loader
from django.core.exceptions import PermissionDenied

from error_pages.template import process_template, process_messages
from error_pages.http import *

import settings


class ErrorPageMiddleware(object):

    def process_exception(self, request, exception):
        '''Process exceptions raised in view code'''
        template = code = response = None

        for i in globals():
            if i.startswith('Http'):
                http_match = isinstance(exception, globals()[i])
                perm_deny = isinstance(exception, PermissionDenied)
                if http_match or perm_deny:
                    if http_match:
                        code = int(i[-3:])
                    elif perm_deny:
                        code = 403

                    template = '%d.html' % code
                    break

        # let django handle these codes instead
        if code in [404, 500]:
            template = code = None

        # ok, now log a warning
        if settings.DEBUG and code:
            # but skip the warning if we have a login form.
            # it is the users job to implement a warning
            # after processing their login
            try:
                if exception.site is None:
                    raise ValueError
            except:
                title = process_messages(code)[0]
                t = []
                for word in title.split(' '):
                    t.append(word.capitalize())
                logging.warning('%s: %s' % (' '.join(t), request.path),
                                extra={
                                    'status_code': code,
                                    'request': request
                                })

        if template is not None:
            if settings.DEBUG:
                TEMPLATE = process_template(code)
                t = Template(TEMPLATE, name='Error Page Template')
            else:
                t = loader.get_template(template)

            response = HttpResponse(t.render(Context({'request': request})), status=code)

        # bring up login form if user wants one
        if code == 401:
            if exception.site:
                response['WWW-Authenticate'] = 'Basic realm="%s"' % exception.site

        return response
