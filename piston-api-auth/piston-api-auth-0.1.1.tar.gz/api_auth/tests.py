import time
import hmac
import hashlib

from django.test import TestCase
from django.conf import settings
from piston.models import Consumer

from api_auth import utils
from api_auth.models import Nonce
import api_auth.authentication as auth


class NamingTest(TestCase):

    def setUp(self):
        settings.API_AUTH_PARAMETERS = {"test1": "test1",
                                        "test2": "test_2",
                                        "test3": "Test-3"}
        settings.API_AUTH_PREFIX = "X-Test-"

    def tearDown(self):
        del settings.API_AUTH_PARAMETERS
        del settings.API_AUTH_PREFIX

    def test_header(self):
        header = utils.header_name("test1")
        self.assertEqual(header, "HTTP_X_TEST_TEST1")
        header = utils.header_name("test2")
        self.assertEqual(header, "HTTP_X_TEST_TEST_2")
        header = utils.header_name("test3")
        self.assertEqual(header, "HTTP_X_TEST_TEST_3")

    def test_parameter(self):
        header = utils.parameter_name("test1")
        self.assertEqual(header, "test1")
        header = utils.parameter_name("test2")
        self.assertEqual(header, "test_2")
        header = utils.parameter_name("test3")
        self.assertEqual(header, "test-3")


class SearchTest(TestCase):

    def setUp(self):
        settings.API_AUTH_PARAMETERS = {"a": "a", "b": "b", "c": "c", "x": "x"}
        settings.API_AUTH_PREFIX = ""

    def tearDown(self):
        del settings.API_AUTH_PARAMETERS
        del settings.API_AUTH_PREFIX

    def test_search_key(self):
        dict1 = {"HTTP_A": 1, "HTTP_B": 2}
        dict2 = {"b": 3, "c": 4}
        value = utils.search_key(dict1, dict2, "a")
        self.assertEqual(value, 1)
        value = utils.search_key(dict1, dict2, "b")
        self.assertEqual(value, 2)
        value = utils.search_key(dict1, dict2, "c")
        self.assertEqual(value, 4)
        self.assertRaises(utils.KeyNotFound, utils.search_key, dict1, dict2, "x")


class TestURI(TestCase):

    def setUp(self):
        settings.API_AUTH_PARAMETERS = {"signature": "sig"}
        settings.API_AUTH_PREFIX = "X-"

    def tearDown(self):
        del settings.API_AUTH_PARAMETERS
        del settings.API_AUTH_PREFIX

    def test_uri(self):
        uri = "http://example.com/?q=1&a=2&b=3"
        normalized_uri = auth.NormalizedUri(uri, {}).get_uri()
        self.assertEqual(normalized_uri, "http://example.com/?a=2&b=3&q=1")

        # The signature argument is removed because it's not present in META
        uri = "http://example.com/?q=1&a=2&b=3&sig=xyz"
        normalized_uri = auth.NormalizedUri(uri, {}).get_uri()
        self.assertEqual(normalized_uri, "http://example.com/?a=2&b=3&q=1")

        # The signature isn't removed because it was present in meta
        uri = "http://example.com/?q=1&a=2&b=3&sig=xyz"
        normalized_uri = auth.NormalizedUri(uri,
                                            {"HTTP_X_SIG": "whatever"}).get_uri()
        self.assertEqual(normalized_uri,
                         "http://example.com/?a=2&b=3&q=1&sig=xyz")

    def test_uri_multiple(self):
        # In case we have multiple parameters with the same name, sort by value
        uri = "http://example.com/?a=1&a=2&b=4&b=3"
        normalized_uri = auth.NormalizedUri(uri, {}).get_uri()
        self.assertEqual(normalized_uri, "http://example.com/?a=1&a=2&b=3&b=4")

        uri = "http://example.com/?a=4&a=2&a=3&a=1"
        normalized_uri = auth.NormalizedUri(uri, {}).get_uri()
        self.assertEqual(normalized_uri, "http://example.com/?a=1&a=2&a=3&a=4")


class TestSecretKey(TestCase):

    def setUp(self):
        # Reuse the consumer from piston for the tests
        settings.API_AUTH_FIELDS = utils.config('fields').copy()
        settings.API_AUTH_APP = "piston"
        settings.API_AUTH_MODEL = "consumer"
        self.c = utils.consumer_model().objects.create(
                    name = "Test", key = "consumer1", secret = "secret1")

    def tearDown(self):
        self.c.delete()
        del settings.API_AUTH_APP
        del settings.API_AUTH_FIELDS

    def test_secret_ok(self):
        consumer = auth.Consumer("consumer1")
        self.assertEquals(consumer.get_secret_key(), "secret1")

    def test_secret_notexist(self):
        consumer = auth.Consumer("consumerx")
        self.assertRaises(auth._AuthException, consumer.get_secret_key)

    def test_secret_multiple(self):
        c = utils.consumer_model().objects.create(
                name = "Test", key = "consumer1", secret = "secret1")
        consumer = auth.Consumer("consumerx")
        self.assertRaises(auth._AuthException, consumer.get_secret_key)
        c.delete()

    def test_secret_invaliddatabase(self):
        settings.API_AUTH_FIELDS["consumer_key"] = "abc"
        consumer = auth.Consumer("consumer1")
        self.assertRaises(auth._AuthException, consumer.get_secret_key)


class TestNonce(TestCase):
    def setUp(self):
        settings.API_AUTH_NONCE = True
        self.n = Nonce.objects.create(consumer_key="consumer1", value="x")

    def tearDown(self):
        del settings.API_AUTH_NONCE
        self.n.delete()

    def test_nonce_valid(self):
        # No exceptions here
        consumer = auth.Consumer("consumer1")
        consumer.validate_nonce("y")
        # This was created as part of the validation process
        Nonce.objects.get(value="y").delete()

    def test_nonce_invalid(self):
        consumer = auth.Consumer("consumer1")
        self.assertRaises(auth._AuthException, consumer.validate_nonce, "x")


class TestSignatureWithoutNonce(TestCase):

    def test_compute_signature(self):
        timestamp = str(int(time.time()))
        uri = "http://example.com/?a=3&b=2&z=1"
        signature = auth.Signature.compute_signature("secret1", "GET", uri,
                                                     timestamp, "consumer1")

        sig_str = "GEThttp://example.com/?a=3&b=2&z=1%sconsumer1" % timestamp
        computed_sig = hmac.HMAC(u"secret1".encode("utf-8"),
                                 sig_str.encode("utf-8"),
                                 hashlib.sha1).hexdigest()
        self.assertEqual(computed_sig, signature)

    #XXX: Add more tests!
