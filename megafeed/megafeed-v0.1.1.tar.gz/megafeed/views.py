from django.http import HttpResponseBadRequest
from django.utils import simplejson as json
import settings, megafeed

def json_feed(request, model=None):
#	if model:
#		model = megafeed.load_model(model)
#		if not model: return megafeed.serial_response(settings.BAD_FEED)
#		prefix = request.REQUEST.get('prefix', settings.DEFAULT_FEED_PREFIX)
#		params = json.loads(request.REQUEST[prefix])
#		return megafeed.serial_response(megafeed.megafeed(model, params, prefix))
#	else:
	response = {}
	for key in request.REQUEST:
		if key != settings.JSONP_PREFIX:
			try: value = json.loads(request.REQUEST[key])
			except: value = {}
			if hasattr(value, '__iter__') and settings.MODEL_SPECIFIER in value:
				model = megafeed.load_model(
					value[settings.MODEL_SPECIFIER])
#				del value[settings.MODEL_SPECIFIER]
			else:
				model = megafeed.load_model(key)
			if not model: response[key] = settings.BAD_FEED
			else:
				response.update(getattr(model, settings.MEGAFEED_ATTR) \
					(params=value, prefix=key, user=request.user))
	return megafeed.serial_response(response)
