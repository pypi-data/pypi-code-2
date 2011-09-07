"""Test suite for delicious services."""

from causal.delicious.service import ServiceHandler
from datetime import date
from causal.main.models import UserService
from django.utils import simplejson
from django.test import TestCase
import feedparser
import os

try:
    import wingdbstub
except ImportError:
    pass

class TestDeliciousService(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.handler = ServiceHandler(model_instance=UserService())
        self.since = date(2011, 7, 26)
        
    def tearDown(self):
        pass
        
    def test_convert_feed(self):
        """Check we get back a correctly formed list of ServiceItems"""
        json_file = open(self.path + '/test_data/user_feed.json', 'r')
        json_feed = json_file.read()
        json_file.close()
        service_items = self.handler._convert_feed(simplejson.loads(json_feed), self.since)
        
        self.assertEqual(len(service_items), 4)
        
    def test_convert_feed_unknown_user(self):
        """Check we get back a correctly formed list of ServiceItems"""
        json_file = open(self.path + '/test_data/unknown_user.json', 'r')
        json_feed = json_file.read()
        json_file.close()
        service_items = self.handler._convert_feed(simplejson.loads(json_feed), self.since)
        self.assertEqual(len(service_items), 0)