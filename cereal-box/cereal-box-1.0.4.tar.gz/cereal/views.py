from django.conf import settings
from django.core.cache import cache
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson as json

import cereal

REQUESTS_TIMEOUT	 = getattr(settings, 'CEREAL_REQUESTS_TIMEOUT', 1)
REQUESTS_PER_TIMEOUT = getattr(settings, 'CEREAL_REQUESTS_PER_TIMEOUT', 15)
SORT_KEYS            = getattr(settings, 'CEREAL_SORT_KEYS', False)

class HttpResponseServiceUnavailable(HttpResponse):
	""" HTTP 503 is Service Unavailable """
	status_code = 503


translate = {ValuesQuerySet:lambda x: list(x)}
def to_json(obj):
	return translate.get(type(obj), str)(obj)

def json_api_timeout(request, model, function):
	ip_address = request.META.get('REMOTE_ADDR',None)
	response = HttpResponseServiceUnavailable()
	if ip_address:
		# Get/Set the number of requests per ip_address
		req_count = cache.get(ip_address, 0) + 1
		cache.set(ip_address, req_count, REQUESTS_TIMEOUT)
		
		# If the req_count is less than the 
		if req_count < REQUESTS_PER_TIMEOUT:
			response = json_api(request, model, function)
	return response

def json_api(request, model, function):
	vars = dict((str(k),v) for k, v in request.REQUEST.iteritems())
	vars.update(dict((str(k), v) for k, v in request.FILES.iteritems()))
	try:
		response = HttpResponse(json.dumps(cereal.call(model, function,
			**vars), default=to_json, sort_keys=SORT_KEYS), mimetype='application/json')
		if settings.DEBUG: response['Cache-Control'] = 'no-cache'
	except KeyError:
		if not settings.DEBUG: 
			raise Http404
		raise 
	return response

def docs(request):
	return render_to_response('cereal/docs.html', {'docs':cereal.docs})
