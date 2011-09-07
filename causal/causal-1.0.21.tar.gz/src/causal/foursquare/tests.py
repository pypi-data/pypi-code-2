"""Test class for Four Square app.
"""

from causal.foursquare.service import ServiceHandler
from datetime import date
from causal.main.models import UserService
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson
import os

try:
    import wingdbstub
except ImportError:
    pass

class TestFoursquareViews(TestCase):
    """Test the module with fixtures.
    """

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.handler = ServiceHandler(model_instance=UserService())

    def tearDown(self):
        pass

    def _loadJson(self, name):
        return simplejson.load(file(os.path.join(self.path, 'test_data', name)))

    def test_convert_feed(self):
        """Check we do the right thing for converting
        foursquares feed into ours."""

        results = self.handler._convert_feed(self._loadJson('checkins.json'), date(2011, 07, 19))

        self.assertEqual(len(results), 12)
        
    def test_badges(self):
        """Test we get back the correct urls for a users badges."""
        
        results = self.handler._pick_badges(self._loadJson('badges.json'), 'projectcausal')
        print results
        #self.assertEqual(len(results), 12)
