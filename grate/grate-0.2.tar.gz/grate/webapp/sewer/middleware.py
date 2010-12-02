from django.template import TemplateSyntaxError
from django.shortcuts import render_to_response
from mongoengine.connection import ConnectionError


class DBExceptionMiddleware(object):

    def process_exception(self, request, exception):
        try:
            if (isinstance(exception, ConnectionError) or
                isinstance(exception.exc_info[0], ConnectionError) or
                str(exception).find('ConnectionError') > 0 or
                str(exception).find('AutoReconnect') > 0):
                # FIXME The string matching is a hack.
                return render_to_response('sewer/dberror.html')
        except:
            pass
