from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from socialtext import Socialtext


# make sure the django project has the proper settings
required_settings = ["ST_URL", "ST_USER", "ST_PASSWORD"]
for s in required_settings:
	if not getattr(settings, s, None):
		raise ImproperlyConfigured("You are using djsocialtext without having set the %s setting." % s)


def get_api(api_cls=Socialtext):
	"""
	Get the Socialtext API client.
	
	:param api_cls: The API class to instantiate. Defaults to socialtext.Socialtext.
					The provided class must accept the Socialtext URL, user, and user
					password as positional arguments.
	"""
	return api_cls(settings.ST_URL, settings.ST_USER, settings.ST_PASSWORD)