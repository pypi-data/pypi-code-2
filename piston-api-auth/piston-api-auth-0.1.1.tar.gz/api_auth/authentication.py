import logging
import time
import urlparse
import hmac
import hashlib
try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl
import urllib

log = logging.getLogger('API_Auth')

from django.http import HttpResponseBadRequest
from django.core.exceptions import FieldError

from api_auth.signals import api_auth_challenge, api_auth_success
from api_auth.signals import api_auth_fail
from api_auth.utils import config, consumer_model, header_name, parameter_name
from api_auth.utils import search_key, KeyNotFound, Override
from api_auth.models import Nonce

class _AuthException(Exception): pass


class HttpSignatureAuthentication(object):
    """
    This class implements signature based authentication for
    Piston APIs.

    Each request will contain the following parameters in the
    HTTP headers section or as query parameters:

    * timestamp - the number of seconds since January 1, 1970 GTM.
    * consumer_key - a key provided by the system to every consumer.
    * signature - a digital signature used to authorize the caller.
    * nonce (optional) - a random generated sequence of characters
      matching the ^[a-zA-Z0-9\-]$ regular expression. This helps
      prevent replay attacks and require additional storage support.

    The string used to compute the signature is created using:

        HTTP verb + normalized URI + request body (if present) +
        + timestamp + consumers key + nonce (if enabled)

    Where:

    * HTTP verb can be GET, POST, etc.
    * normalized URI is created by sorting the UTF-8 encoded query
      string with natural byte ordering.
    * request body the raw POST data if present.

    The signature is created using RFC 2104-compliant HMAC using
    SHA1 as the hash algorithm. The value used to sign the request
    is the hexadecimal representation of the actual signature.

    There are a number of options available to customize the way
    authentication works:

    * API_AUTH_APP - sets the name of the application containing
      the consumer model.

    * API_AUTH_MODEL - the name of the model class representing the
      consumer model (defaults to 'consumer').

    * API_AUTH_FIELDS - the name of the fields used in the model to
      represent the consumer_key and consumer_secret (defaults
      to {'consumer_key':'key','consumer_secret':'secret'}).

    * API_AUTH_PARAMETERS - a mapping of parameter names used as
      query parameters and/or HTTP headers (defaults to
      {'timestamp': 'timestamp', 'consumer_key': 'consumer_key',
       'signature': 'signature', 'nonce': 'nonce'}).

      Note:
      For header parameters each '-' is automatically replaced by
      a '_' and the name is case insensitive. This means that when
      using header parameters 'Header-Name' and 'HEADER_NAME' are
      equivalent.
      In contrast the parameters sent as query arguments must allways
      be lowercased.

    * API_AUTH_PREFIX - used to prefix parameter names when
      transmited as headers.

    * API_AUTH_NONCE - boolean flag indicating whether to use or
      not the nonce (useful against reply attacks).

    * API_AUTH_TIMEOUT - the maximum age in seconds a request can have
      to be considered valid.

    A couple of signals are emitted if the authentication process
    is successful or not. For more documentation see signals.py.
    """

    def fail(self, request):
        override_consumer = Override()
        api_auth_fail.send(sender=self.__class__,
                           request=request,
                           override_consumer=override_consumer)
        if override_consumer.data:
            api_auth_success.send(sender=self.__class__,
                                  request=request,
                                  consumer_key=override_consumer.data)
            return True
        return False

    def check_nonce(self, meta, get, consumer_key):
        if config('nonce'):
            nonce = search_key(meta, get, 'nonce')
            consumer = Consumer(consumer_key)
            consumer.validate_nonce(nonce)

    def is_authenticated(self, request):
        """
        This method is required by Piston to implement custom
        authentication protocol.
        It must return True if the authentication is successful.
        It's also good practice to set request.user and other fields
        to certain values that can be used in other places.
        In case the authentication was successful a signal is emitted
        to allow further customisation.
        """
        try:
            incoming = Signature.extract_from_request(request)
            computed = Signature.compute_from_request(request)
            if not incoming == computed:
                msg = "Signatures don't match. Expecting %s." % computed
                return self.handle_error(msg, request)
            consumer_key = search_key(request.META, request.GET, 'consumer_key')
            # Check the nonce last so we minimize the db hit.
            self.check_nonce(request.META, request.GET, consumer_key)
        except (_AuthException, KeyNotFound), e:
            return self.handle_error(e, request)

        api_auth_success.send(sender=self.__class__,
                              request=request,
                              consumer_key=consumer_key)
        return True

    def handle_error(self, error, request):
        log.warning(str(error))
        return self.fail(request)

    def challenge(self):
        """
        This method is called if the authentication is unsuccessful.
        It returns a standard BadRequest response and emits a signal.
        The response can be modified by intercepting the signal and
        appending a custom response object to 'custom_response' list.
        """
        response = HttpResponseBadRequest("Authorisation failed.")
        override_response = Override()
        api_auth_challenge.send(sender=self.__class__,
                                override_response=override_response)
        return override_response.data or response


class NormalizedUri(object):
    """
    Normalized URI is created by sorting the UTF-8 encoded query
    string with natural byte ordering.
    The signature is removed if it's present in the uri.
    """

    def __init__(self, uri, meta):
        self.uri = uri
        self.meta = meta

    def signature_in_meta(self):
        """
        Verifies if the signature is sent in the header.
        """
        return header_name('signature') in self.meta

    def get_uri(self):
        url_pieces = urlparse.urlparse(self.uri)
        qsl = parse_qsl(url_pieces.query)
        if not self.signature_in_meta():
            # Remove the signature from the querystring.
            sig_parameter = parameter_name('signature')
            qsl = [q for q in qsl if not q[0] == sig_parameter]
        qsl.sort()
        pieces = list(url_pieces)
        pieces[4] = urllib.urlencode(qsl)
        normalized_uri = urlparse.ParseResult(*pieces).geturl()
        return normalized_uri


class Consumer(object):

    def __init__(self, consumer_key):
        self.consumer_key = consumer_key

    def get_secret_key(self):
        """
        Queries the database to find the secret key for this consumer.
        """
        fields = config('fields')
        ConsumerModel = consumer_model()
        query = {fields['consumer_key']: self.consumer_key}
        try:
            q = ConsumerModel.objects.values(fields['consumer_secret'])
            consumer_secret = q.get(**query)
        except FieldError:
            raise _AuthException("Invalid database fields.")
        except ConsumerModel.DoesNotExist:
            raise _AuthException("Invalid consumer key: %s." % self.consumer_key)
        except ConsumerModel.MultipleObjectsReturned:
            raise _AuthException(
                "Invalid database. "
                "Consumer keys are not unique: %s." % self.consumer_key
            )
        return consumer_secret[fields['consumer_secret']]

    def validate_nonce(self, nonce):
        """
        A nonce is invalid if it was already used by a consumer more than
        once in a timeframe smaller than API-AUTH-TIMEOUT.
        In case API_AUTH_NONCE is False we don't use nonces.
        """
        # Check to see if nonces are activated.
        if not config('nonce'):
            return
        try:
            Nonce.valid.get(consumer_key=self.consumer_key, value=nonce)
            # If the object already exists it's invalid.
            raise _AuthException("Nonce %s already exists." % nonce)
        except Nonce.DoesNotExist:
            # If the nonce is unique for this timeframe, create one.
            Nonce.objects.create(consumer_key=self.consumer_key, value=nonce)


class Signature(object):

    def __init__(self, signature):
        self.signature = signature

    @staticmethod
    def extract_from_request(request):
        """
        Search for signature in headers and in get arguments.
        """
        try:
            sig = search_key(request.META, request.GET, 'signature')
        except KeyNotFound:
            raise _AuthException("Signature not found in request.")
        return Signature(sig)

    @staticmethod
    def compute_from_request(request):
        """
        Computes the signature based on the data stored in request object.
        """
        verb = request.method
        absolute_uri = request.build_absolute_uri()
        uri = NormalizedUri(absolute_uri, request.META).get_uri()
        try:
            timestamp = search_key(request.META, request.GET, 'timestamp')
            consumer_key = search_key(request.META, request.GET, 'consumer_key')
            nonce = None
            if config('nonce'):
                nonce = search_key(request.META, request.GET, 'nonce')
        except KeyNotFound:
            raise _AuthException("Invalid Request. Some arguments are missing.")
        # A request is timedout if its life is longer than the value specified
        # in API_AUTH_TIMEOUT.
        try:
            if int(time.time()) > int(timestamp) + config('timeout'):
                raise _AuthException("The request has timed out. "
                                    "Expected timestamp: %s." % int(time.time()))
        except ValueError:
            raise _AuthException("Invalid timestamp format. Must be integer.")
        body = request.raw_post_data
        consumer = Consumer(consumer_key)
        secret = consumer.get_secret_key()
        signature = Signature.compute_signature(secret, verb, uri, timestamp,
                                                consumer_key, body, nonce)
        return Signature(signature)

    @staticmethod
    def compute_signature(secret, verb, uri, timestamp, consumer_key,
                          body=None, nonce=None):
        """
        The string used to compute the signature is created using:

        HTTP verb + normalized URI + request body (if present) +
        + timestamp + consumers key + nonce (if enabled)
        """
        sig_string = verb + uri
        if body:
            sig_string += body
        sig_string += timestamp + consumer_key
        if nonce:
            sig_string += nonce
        return hmac.HMAC(secret.encode('utf-8'),
                         sig_string.encode('utf-8'),
                         hashlib.sha1).hexdigest()

    def __eq__(self, other):
        """
        Compares the signatures in a way that is safe against timing attacks.
        I think this is to elite because if you have a relatively small
        timeout it should be enough but it's better to have it than to
        be sorry later.
        """
        authenticated = len(self.signature) == len(other.signature)
        if authenticated:
            for left, right in zip(self.signature, other.signature):
                if left != right:
                    authenticated = False
        return authenticated

    def __str__(self):
        return self.signature
