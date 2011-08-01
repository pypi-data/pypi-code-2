from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson as json
from django.conf import settings

import cereal

translate = {ValuesQuerySet:lambda x: list(x)}
def to_json(obj):
	return translate.get(type(obj), str)(obj)

def json_api(request, model, function):
	vars = dict((str(k),v) for k, v in request.REQUEST.iteritems())
	vars.update(dict((str(k), v) for k, v in request.FILES.iteritems()))
	try:
		response = HttpResponse(json.dumps(cereal.call(model, function,
			**vars), default=to_json), mimetype='application/json')
		if settings.DEBUG: response['Cache-Control'] = 'no-cache'
	except KeyError:
		if not settings.DEBUG: 
			raise Http404
		raise 
	return response

def docs(request):
	return render_to_response('cereal/docs.html', {'docs':cereal.docs})
