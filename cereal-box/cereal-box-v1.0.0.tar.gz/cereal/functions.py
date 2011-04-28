import cereal

def managerize(function):
	"""
	Decorator to parameterize the manager in functions.
	Usage:
		cereal.register(Model, [function()]) # Defaults to _default_manager
		cereal.register(Model, [function('objects')])
	"""
	fn_name = function.__name__
	def manager_fn(manager='_default_manager'):
		def inner_fn(model, **kwargs):
			return function(model, manager, **kwargs)
		inner_fn.__name__ = fn_name
		inner_fn.__doc__  = function.__doc__
		return inner_fn
	return manager_fn

@managerize
def list(model, manager):
	"""
	Returns a list of %(model)ss (max 100 results).
	"""
	return cereal.ize(getattr(model, manager).all()[:100])

@managerize
def filter(model, manager, **kwargs):
	"""
	Filter on %(model)s by %(properties)s (max 100 results).

	Additional arguments:
	sort - Sort by %(properties)s (prepend - to reverse)
	"""
	sort = kwargs.get('sort', None)
	if 'sort' in kwargs: del kwargs['sort']
	ret = getattr(model, manager).filter(**kwargs)
	if sort: ret = ret.order_by(sort)
	return cereal.ize(ret)

@managerize
def page_filter(model, manager, **kwargs):
	"""
	Filter on %(model)s by %(properties)s

	Additional arguments:
	sort     - Sort by %(properties)s (prepend - to reverse)
	per_page - Number of results (up to 100)
	page     - Current page number (starting at 1)
	"""
	sort = kwargs.get('sort', None)
	per_page = int(kwargs.get('per_page', 10))
	if per_page > 100 or per_page < 1: per_page = 100
	page = int(kwargs.get('page', 1))
	if 'sort' in kwargs:     del kwargs['sort']
	if 'page' in kwargs:     del kwargs['page']
	if 'per_page' in kwargs: del kwargs['per_page']
	if page < 1: page = 1
	offset = page*per_page
	ret      = getattr(model, manager).filter(**kwargs)
	if sort: ret = ret.order_by(sort)
	count    = ret.count()
	return {'total' : ret.count(),
			'items' : cereal.ize(ret[offset-per_page:offset])}
