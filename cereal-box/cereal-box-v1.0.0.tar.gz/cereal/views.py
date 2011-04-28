from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson as json

import cereal

translate = {ValuesQuerySet:lambda x: list(x)}
def to_json(obj):
	return translate.get(type(obj), str)(obj)

def json_api(request, model, function):
	vars = dict((str(k),v) for k, v in request.REQUEST.iteritems())
	vars.update(dict((str(k), v) for k, v in request.FILES.iteritems()))
	return HttpResponse(json.dumps(cereal.call(model, function,
		**vars), default=to_json), mimetype='application/json')

def docs(request):
	return render_to_response('cereal/docs.html', {'docs':cereal.docs})
