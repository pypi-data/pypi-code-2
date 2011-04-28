def values(include=None):
	"""
	Usage:
		cereal.register(Model, [], serializer=values())
		cereal.register(Model, [], serializer=values(['id', 'name']))
	"""
	include = include or []
	def values_fn(queryset):
		"""
		Serializer to values(*%s) of queryset
		""" % include
		return queryset.values(*include)
	return values_fn
