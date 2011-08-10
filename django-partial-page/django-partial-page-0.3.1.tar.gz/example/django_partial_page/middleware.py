from functools import wraps
from threading import local

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json


PARTIAL_PARAM_NAME = getattr(settings, 'PARTIAL_PARAM_NAME', 'partial')
_thread_locals = local()


class PartialPageMiddleware(object):
	"""
	Catches the requests for partial pages and saves all the named blocks in a dictionary, then sends the dictionary as JSON.

	Notes: this middleware will catch the blocks contents at the moment they are rendered, no matter who calls response.render(). But if other middleware classes replace the response contents (say, redirect links to a counter), these changes can't be saved in the dictionary.
	"""
	def __init__(self):
		"""
		Monkey patches BlockNode so that if block name is requested in GET parameters,
		it will be saved in _thread_locals and sent in JSON response.
		"""
		from django.template.loader_tags import BlockNode

		# here we stick our nose into block node:
		# we capture its return value and save it into a dictionary
		real_render = BlockNode.render

		def new_render(self, context):
			result = real_render(self, context)
			if not _thread_locals.request.no_partial and self.name in getattr(_thread_locals.request, 'partials', []):  # save the block contents if it's requested in GET
				_thread_locals.partial['blocks'][self.name] = result  # this overwrites the existing value, but that's ok, since the final block is what is shown in the rendered template.
			return result

		BlockNode.render = new_render

	def process_view(self, request, callback, callback_args, callback_kwargs):
		"""
		Tests if partial parameter is in GET parameters and extracts block names from it.
		"""
		_thread_locals.request = request
		request.no_partial = callback_kwargs.pop('no_partial', False)
		request.partials = []
		if not request.no_partial and PARTIAL_PARAM_NAME in request.GET:
			request.partials = request.GET[PARTIAL_PARAM_NAME].split(',')

		_thread_locals.partial = {'blocks': {}, 'data': {}}

	def process_response(self, request, response):
		"""
		Bypasses the response or, if partial page is requested, returns JSON.
		"""
		if getattr(request, 'no_partial', False) or len(getattr(request, 'partials', [])) == 0:
			return response

		json_obj = dict(
			(key, _thread_locals.partial[key])
			for key in ['blocks', 'data']
			if len(_thread_locals.partial[key]) > 0
		)
		
		new_response = HttpResponse(json.dumps(json_obj), mimetype='application/json')
		new_response.status_code = response.status_code
		return new_response


def set_js_data(**kwargs):
	"""
	Updates the `data` dictionary in the json object that partial middleware sends.
	"""
	_thread_locals.partial['data'].update(kwargs)


def no_partial(func):
	"""
	A decorator that protects a view from partial page requests.
	(Unless the view itself overrides this.)
	"""
	@wraps(func)
	def _decorated(request, *args, **kwargs):
		request.no_partial = True
		return func(request, *args, **kwargs)
	return _decorated
