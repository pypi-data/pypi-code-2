#from django.core.paginator import Paginator, Page
import math, settings

# python 2.5 patch
try: import hashlib
except: import md5 as haslib

feeds = {}
feeds_secure = {}
feeds_cache = {}

class Page:
	def __init__(self, queryset, page=1, per_page=10, start=0):
		self.number    = page
		self.per_page  = per_page
		self.start     = start
		self.count     = queryset.count()
		self.num_pages = int(math.ceil(float(self.count-start)/self.per_page))
		self.page_range= range(1,self.num_pages+1)
		fro = per_page*(page - 1) + start
		self.object_list = queryset[fro: fro+per_page]
	@property
	def paginator(self): return self

class SerialDict(dict): # Hack for wrapping dicts in XML
	def __init__(self, xml_wrapper, *args, **kwargs):
		super(SerialDict, self).__init__(*args, **kwargs)
		self.xml_wrapper = xml_wrapper

	#Handle pagination with a generic list of items, can accept a prefix
	#page_params needs to support get('key', 'default')
def page_of(list, page_params, page=1, per_page=10, start=0):
	#TODO: rewrite below with more proper handling?
	try: page = int(page_params.get(settings.PAGE_PREFIX, page))
	except: pass
	try: per_page = int(page_params.get(settings.PER_PAGE_PREFIX, per_page))
	except: pass
	try: start = int(page_params.get(settings.START_PREFIX, start))
	except: pass

	return Page(list, page, per_page, start)

#	paginator = Paginator(list, per_page)
#	try: result = paginator.page(page)
#	except: result = paginator.page(paginator.num_pages)
#	return result

def to_dict(object, *args, **kwargs):
	if hasattr(object, '__iter__'):
		return [getattr(item, settings.TO_DICT_ATTR)(*args, **kwargs) for item in object]
	else:
		return getattr(object, settings.TO_DICT_ATTR)(*args, **kwargs)

def merge(params, query, can_override=False):
	if can_override:
		for k in query: params[k] = query[k] 
	else:
		for k in query:
			if not k in params: params[k] = query[k] 
	return params

from django.core.cache import cache
#from django.utils import simplejson as json #Conflicts with Django's encoder later

@classmethod
def megafeeder(type, params = None, request_params = None, prefix = '',
		 defaults = None, can_override=False, **kwargs):
	"""
	Returns a megafeed with appropriate parameters set

	type           -- The calling class (@classmethod)
	params         -- A dictionary of values to be passed into filter()
	request_params -- A QueryDict containing (PREFIX_)key:value pairs
	prefix         -- The root element of the dictionary
	defaults       -- Default values to supplement either params
	can_override   -- Whether the default values can be overriden
	"""
	if not prefix:
		prefix = type.__name__.lower()
	params = params or {}
	if request_params:
		for key in request_params:
			if ('%s_' % key).startswith(prefix):
				params[key[len(prefix)+1:]] = request_params[key]
	if defaults:
		params = merge(defaults, params, can_override=can_override)
	return megafeed(type, params=params, prefix=prefix, **kwargs)

def megafeed(type, params=None, prefix='', cache_time=0,
		user=None, to_dict=to_dict, **kwargs):
	"""
	Returns a paginated dictionary of the calling type

	type       -- The class to serialize
	params     -- A dictionary of values to be passed into filter()
	prefix     -- The root element of the dictionary
	cache_time -- If defined, this feed will be cached for this many seconds
	paginate   -- Whether to paginate (and include pagination data)
	to_dict	   -- Called with the returned queryset (or False)
	"""
	#print params
	############   Python Unicode Dict Hack   ##############
	d = {}
	if hasattr(params, '__iter__'):
		for k in params:
			d[str(k)] = params[k]
	params = d
	############  /Python Unicode Dict Hack   ##############
	
	value = None
	if not prefix:
		prefix = type.__name__.lower()

	if not cache_time and type in feeds_cache:
		cache_time = feeds_cache[type]

	if cache_time:
		key = hashlib.md5(''.join(['%s=%s' % (k, hasattr(params[k], 'id')
				 and str(params[k].id) or str(params[k])) for k in
				 sorted(params.keys())]) + type.__name__).hexdigest()
		value = cache.get(key)
	if not value:
		queryset = getattr(type, settings.FILTER_ATTR)(_user=user, **params)
		set_page = settings.PAGINATE_ARG in params
		if set_page and params[settings.PAGINATE_ARG] or not set_page:
			queryset = page_of(queryset, params)
			value = {prefix: {'page_data': {
				'page_range': queryset.paginator.page_range,
				'page_count': queryset.paginator.num_pages,
				'per_page': queryset.paginator.per_page,
				'object_count': queryset.paginator.count,
				'current_page': queryset.number}, 'filter_list': params,
				'object_list': to_dict and to_dict(queryset.object_list,
					**params) or list(queryset.object_list),
				'type': type.__name__.lower()}}
		elif settings.DEFAULT_PAGINATE or settings.PER_PAGE_PREFIX in params\
		 	 	or settings.PAGE_PREFIX in params or settings.START_PREFIX in params:
			if settings.PER_PAGE_PREFIX in params:
				per_page = params[settings.PER_PAGE_PREFIX]
			else: per_page = 100
			if settings.PAGE_PREFIX in params:
				page = params[settings.PAGE_PREFIX] or 1
			else: page = 1
			value = {prefix: {'page_data': {
				'per_page': per_page,
				'current_page': page}, 'filter_list': params,
				'object_list': to_dict(queryset[(page-1)*per_page:page*per_page], **params),
				'type': type.__name__.lower()}}
			if settings.START_PREFIX in params:
				start = params[settings.START_PREFIX]
				value[prefix]['page_data']['start'] = start
		else:
			value = {prefix: { 'object_list': to_dict(queryset, **params),
							   'type': type.__name__.lower()}}
		if cache_time:
			cache.set(key, value, cache_time)
	return value

def xml_serialize(obj):
	# Not sure about this line, requires additional imports
	# if isinstance(obj, QuerySet) or isinstance(obj, MultiDBQuerySet):
	#	  obj = to_dict(obj.to_dict)
	if hasattr(obj, 'xml_wrapper') and obj.xml_wrapper:
		wrapper = obj.xml_wrapper
		del obj.xml_wrapper
		obj = {wrapper: obj}
	if isinstance(obj, dict):
		return ''.join(['<%(node)s>%(value)s</%(node)s>' % {'node': key,
				 'value': xml_serialize(obj[key])} for key in obj])
	elif isinstance(obj, list):
		return ''.join([xml_serialize(i) for i in obj])
	elif isinstance(obj, tuple):
		return ''.join([xml_serialize(i) for i in obj])
	elif isinstance(obj, bool):
		return obj and 1 or 0
	elif obj == None:
		return ''
	elif isinstance(obj, basestring):
		return '<![CDATA[%s]]>' % unicode(obj)
	else: return unicode(obj)

def serial_response(obj):
	return {'response':obj}

from django.db.models.fields.related import ForeignKey

def default_to_dict(self, *args, **kwargs):
	ret, expand, level = {}, [], 0

	if settings.EXPAND_RELATED in kwargs: expand = kwargs[settings.EXPAND_RELATED]
	for field in self._meta.fields:
		if isinstance(field, ForeignKey):
			ret[field.name] = {}
			for k in feeds:
				if feeds[k] == field.related.parent_model:
					ret[field.name]['feed'] = k
					if field.name in expand and hasattr(getattr(self,
							field.name), settings.TO_DICT_ATTR):
						if expand:
							kwargs[settings.EXPAND_RELATED] = [e.split('.', 1)[1]
								for e in expand if e.startswith(field.name + '.')]
						ret[field.name].update(getattr(getattr(
						   self, field.name), settings.TO_DICT_ATTR)(**kwargs))
#						   **dict([(k.split('.', 1)[1], kwargs[k])
#						   for k in kwargs if '.' in k])))#if k.startswith(field.name+'.')])))
					else:
						ret[field.name]['id'] = getattr(self, field.name + '_id')
					break
			if not ret[field.name]:
				ret[field.name]['id'] = getattr(self, field.name + '_id')
		else:
			field_value = getattr(self, field.name)
			name = '%s.%s' % (type(field_value).__module__, type(field_value).__name__)

			if name in settings.TO_DICT_FN:
				field_value = settings.TO_DICT_FN[name](field_value)
			ret[field.name] = field_value
	return SerialDict(self.__class__.__name__.lower(), ret)

from django.db.models import Q

def check_field(key):
	if '.' in key:
		check = key.split('.')[0]
		field = key.replace('.', '__')
	else:
		check = field = key
	return check, field

def filter(cls, _objects=None, _user=None, **kwargs):
	if _objects is None: _objects = cls.objects.all()
	try:
		options = cls._meta._name_map
	except AttributeError:
		options = cls._meta.init_name_map()
	except: options = [f.name for f in cls._meta.fields()]
	
	filters = {}
	excludes = {}
	for key, value in kwargs.iteritems():
		if key == settings.ORDERING:
			_objects = _objects.order_by(*value.split(','))
			continue
		if key == settings.OR_QUERY:
			if not isinstance(value, list): value = [value]
			for o in value:
				q_q  = None
				for k,v in o.iteritems():
					check, field = check_field(k)
					field = str(field)
					if check in options:
						if q_q: q_q = q_q|Q(**{field:v})
						else:   q_q = Q(**{field:v})
				if q_q: _objects = _objects.filter(q_q)
				#print q_q
			continue
		negate = False
		if key[0] in ['-']:
			negate = True
			key = key[1:]
		check, field = check_field(key)
		if check in options:
			if negate: excludes[field] = value
			else: filters[field] = value
	
	_objects = _objects.filter(**filters).exclude(**excludes)
			
	if cls in feeds_secure:
		_objects = _objects.filter(**{feeds_secure[cls]:_user.id})
	if kwargs.get(settings.DISTINCT_ATTR, settings.DEFAULT_SELECT_DISTINCT):
		_objects = _objects.distinct()
	
	return _objects

default_filter = classmethod(filter)

def register(model, filter=None, name=None, secure=None, cache_time=0):
	if hasattr(model, '__iter__'):
		for i in model:
			if isinstance(i, dict): register(**i)
			else:				   register(i)
		return

	if name:
		name = name.lower()
	else:
		name = model.__name__.lower()
	if name in feeds:
		raise ValueError('%s is already registered.' % name)
	feeds[name] = model
	if not hasattr(model, settings.TO_DICT_ATTR):
		setattr(model, settings.TO_DICT_ATTR, default_to_dict)
	if not hasattr(model, settings.FILTER_ATTR):
		setattr(model, settings.FILTER_ATTR, filter or default_filter)
	if not hasattr(model, settings.MEGAFEED_ATTR):
		setattr(model, settings.MEGAFEED_ATTR, megafeeder)

	if secure:
		feeds_secure[model] = secure
	if cache:
		feeds_cache[model] = cache_time

def load_model(model):
	try: return feeds[model]
	except KeyError: return None

 ### Extension methods ###

@classmethod
def tagging_filter(cls, _user=None, **kwargs):
	objects = None
	if settings.ANY_TAGS_ATTR in kwargs:
		objects = cls.tagged.with_any(kwargs[settings.ANY_TAGS_ATTR])
	elif settings.ALL_TAGS_ATTR in kwargs:
		objects = cls.tagged.with_all(kwargs[settings.ALL_TAGS_ATTR])
	return filter(cls, objects, _user, **kwargs)
