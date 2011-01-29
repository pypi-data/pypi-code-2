import unittest

# import base first because sys.path is changed in order to find amazonproduct!
from base import XMLResponseTestCase, XMLResponseTestLoader
from base import XML_TEST_DIR, TESTABLE_API_VERSIONS

# load base with its import magic before amazonproduct
from base import AWS_KEY, SECRET_KEY

from amazonproduct.contrib.caching import ResponseCachingAPI, DEFAULT_CACHE_DIR

class CachingTestCase (unittest.TestCase):

    def setUp(self):
        self.api = ResponseCachingAPI(AWS_KEY, SECRET_KEY, 'de')

    def test_caching_works(self):
        self.api.item_search('Books', Publisher='Galileo Press')