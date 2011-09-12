def templates_list(name, obj):
	return [
		'%s/%s/%s' % (obj._meta.app_label, obj.__class__.__name__, name),
		'%s/%s' % (obj._meta.app_label, name),
		name,
	]
