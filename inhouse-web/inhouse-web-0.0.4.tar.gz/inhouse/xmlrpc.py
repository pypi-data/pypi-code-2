# -*- coding: utf-8 -*-

import sys

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse, HttpResponseServerError

from decorators import post_required
import models

if sys.version_info[:3] >= (2,5,):
    dispatcher = SimpleXMLRPCDispatcher(allow_none=True, encoding=None)
else:
    dispatcher = SimpleXMLRPCDispatcher()

@post_required
def handle_xmlrpc(request):
    if settings.DEBUG:
        print request.raw_post_data
    response = HttpResponse(mimetype="application/xml")
    try:
        response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
    except Exception, e:
        return HttpResponseServerError()
    response['Content-length'] = str(len(response.content))
    return response

def bookings():
    query = models.Booking.objects.all()
    data = serializers.serialize('json', query)
    return HttpResponse(data, mimetype='application/json')


dispatcher.register_function(bookings, 'bookings')