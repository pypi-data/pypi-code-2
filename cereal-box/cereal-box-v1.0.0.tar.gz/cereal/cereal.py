import logging

import serializers

models  = {} # {'model':Model}
serials = {} # {'model':json.dumps}, name conflict with serializers
funcs   = {} # {'model':{'filter':Model.filter}}, name conflict with functions
docs    = {} # {'model':{'filter':'Docstring'}}, hack for Django 1.3

red   = lambda message: '\033[1;31m%s\033[0m' % message
green = lambda message: '\033[1;32m%s\033[0m' % message

def register(model, functions, serializer=None):
	"""
	Registers a model with cereal-box.
	model     - The model in question.
	functions - A list of callable functions e.g.
		def filter(model, **kwargs): return model.objects.filter(**kwargs)
	serial    - An optional queryset serializer.
	"""
	name = model.__name__.lower()
	if name in models:
		logging.warning('Model %s already registered with cereal-box',
				red(model.__name__))
	models[name]  = model
	serials[name] = serializer or serializers.values()
	funcs[name]   = {}
	docs[name]    = {}
	for fn in functions:
		fn_name = fn.__name__.lower()
		if fn_name in funcs[name]: logging.warning(
			'Function [%s] already registered on model [%s] with cereal-box',
			red(fn_name), red(model.__name__))
		else:
			if fn.__doc__: fn.__doc__ = fn.__doc__ % {'model':model.__name__,
				'properties': ', '.join([f.name for f in model._meta.fields])}
			docs[name][fn_name] = fn.__doc__ or 'Edit this function\'s docstring to customize this line.'
			funcs[name][fn_name] = fn
			logging.debug('Registered %s on %s',
					green(fn_name), green(model.__name__))

def call(model, function, **kwargs):
	"""
	Calls a function on a registered model.
	model    - The name of the model.
	function - The name of the function.
	**kwargs - Function parameters.
	"""
	logging.debug('%s.%s called with arguments %s' % (model, function ,kwargs))
	return funcs[model][function](models[model], **kwargs)

def ize(queryset):
	"""
	Calls the appropriate serialize on a queryset.
	"""
	return serials[queryset.model.__name__.lower()](queryset)
