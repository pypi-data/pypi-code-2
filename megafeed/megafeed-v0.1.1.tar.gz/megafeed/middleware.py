from django.utils import simplejson
from django.core.serializers import json
from django.http import HttpResponse
import settings
from megafeed import *


class MegaMiddleware(object):
	def process_response(self, request, response):
		if isinstance(response, HttpResponse):
			return response
		if settings.SHOW_QUERIES:
			from django.db import connection
			response['queries'] = connection.queries

		if request.path.endswith('xml'):
			return HttpResponse(xml_serialize(response), mimetype='application/xml')
		elif settings.JSONP_PREFIX in request.REQUEST:
			return HttpResponse(request.REQUEST[settings.JSONP_PREFIX] + '('
				+ simplejson.dumps(response, cls=json.DjangoJSONEncoder,
				ensure_ascii=False, default=settings.JSON_DEFAULT) + ')',
				mimetype='application/javascript')
		else:
			return HttpResponse(simplejson.dumps(response,
					cls=json.DjangoJSONEncoder, ensure_ascii=False,
					default=settings.JSON_DEFAULT), mimetype='application/json')
