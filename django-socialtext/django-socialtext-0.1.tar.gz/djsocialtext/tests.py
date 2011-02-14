from django.conf import settings
from django.test import TestCase

class DummyClient(object):
	"""
	Dummy HTTP client for the DummyApi
	"""
	def __init__(self, server, user, password):
		self.server = server
		self.user = user
		self.password = password

class DummyApi(object):
	"""
	A dummy API class
	"""	
	def __init__(self, server, user, password):
		self.client = DummyClient(server, user, password)

class ApiTestCase(TestCase):

	def test_get_api(self):
		from djsocialtext import get_api

		api = get_api()

		# the API client should have the proper settings
		self.assertEqual(settings.ST_URL, api.client.server)
		self.assertEqual(settings.ST_USER, api.client.user)
		self.assertEqual(settings.ST_PASSWORD, api.client.password)

		# test that the method will use an injected class
		api = get_api(api_cls=DummyApi)
		self.assertTrue(isinstance(api, DummyApi))