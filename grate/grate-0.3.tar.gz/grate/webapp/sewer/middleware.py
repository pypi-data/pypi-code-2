from django.shortcuts import render_to_response
from mongoengine.connection import ConnectionError
from pymongo.errors import AutoReconnect


class DBExceptionMiddleware(object):

    def process_exception(self, request, exception):
        try:
            if (isinstance(exception.exc_info[1], ConnectionError) or
                isinstance(exception.exc_info[1], AutoReconnect) or
                isinstance(exception, ConnectionError) or
                isinstance(exception, AutoReconnect)):
                return render_to_response('sewer/dberror.html')
        except:
            pass
