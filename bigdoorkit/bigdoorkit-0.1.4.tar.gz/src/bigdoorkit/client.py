import restkit
import hashlib
try:
    import json
except ImportError, e:
    import simplejson as json

from uuid import uuid4
from time import time as unix_time
from urllib import urlencode
from exc import PayloadError

__all__ = ["Client"]

class Client(object):
    """Requires `app_secret` and `app_key` as supplied by BigDoor.
    Optional `api_host` parameter allows for use with API compatible
    services and/or staging servers.
    """
    def __init__(self, app_secret, app_key, api_host=None):
        """Constructor for a `Client` object.

        Parameters:
            - app_secret string The API secret supplied by BigDoor

            - app_key string The API key supplied by BigDoor

            - api_host string An alternative host to enable use with testing
            servers.
        """
        self.app_secret = app_secret
        self.app_key = app_key
        if not api_host:
            api_host = "http://api.bigdoor.com"
        self.api_host = api_host
        self.base_url = "/api/publisher/%s" % self.app_key
        self.conn = restkit.Resource(self.api_host)

    def generate_token(self):
        """Helper method
        """
        return uuid4().hex

    def generate_signature(self, url, params=None, payload=None):
        """Generates the appropriate signature given a url and optional
        params."""
        sig = url
        if params:
            sig += self._flatten_params(params)
        if payload:
            sig += self._flatten_params(payload)
        sig += self.app_secret
        return hashlib.sha256(sig).hexdigest()

    def _flatten_params(self, params):
        """Flattens a parameter dictionary for signature generation"""
        return ''.join(["%s%s" % (k, params[k])
                        for k in sorted(params.keys())
                        if k not in ('sig', 'format')])

    def _sign_request(self, method, url, params=None, payload=None):
        """Algorithm to sign a request as per the BigDoor documentation. Adds
        defaults to `params` and `payload` if not present.

        Parameters:
            - method string The HTTP method for the request

            - url string The full URL, including the base /api/publisher/[app_key]

            - params dict The parameters to be sent via the GET query string

            - payload dict The data to be sent via the POST body
        """
        if params is None:
            params = {}
        is_postish = method in ['post', 'put']

        # The payload time is assumed to be the correct value
        if is_postish and 'time' in payload:
            params['time'] = payload['time']
        if not 'time' in params:
            params['time'] = str(unix_time())
        if is_postish and not 'time' in payload:
            payload['time'] = params['time']

        if is_postish and not 'token' in payload:
            payload['token'] = self.generate_token()

        if method == 'delete' and not 'delete_token' in params:
            params['delete_token'] = self.generate_token()

        params['sig'] = self.generate_signature(url, params, payload)
        return params, payload

    def _abs_from_rel(self, url):
        """Private helper method to concatenate the base url and endpoint.
        """
        return "%s/%s" % (self.base_url, url)

    def do_request(self, method, endpoint, params=None, payload=None):
        """Sends a request to the API, signing it before it is sent.
        Returns a restkit response object.

        Parameters:
            - method string The HTTP method to use for the request. Can be one
            of ['get', 'delete', 'post', 'put']. Note: case of the string does
            not matter.

            - endpoint string The relative URI that comes directly after
            your API key in the BigDoor documentation.

            - params dict The parameters to be sent via the GET query string.

            - payload dict The data to be sent via the POST body
        """
        # Copy the parameters and payload variables so we don't pollute passed
        # dictionaries with auto-generated API information.
        par = {}
        pay = {}

        if params is not None:
            par = params.copy()
        if payload is not None:
            pay = payload.copy()

        method = method.lower()
        if method in ['post', 'put'] and not isinstance(pay, dict):
            err_msg = "Payload must be <type 'dict'>, not %s" % type(pay)
            raise PayloadError(err_msg)
        url = self._abs_from_rel(endpoint)
        par, pay = self._sign_request(method, url, par, pay)
        func = getattr(self.conn, method)
        print url
        if method in ['post', 'put']:
            par['payload'] = pay

        return func(url, **par)

    def get(self, endpoint, params=None):
        """Sends a GET request to the API and returns a native data
        structure from the JSON response.

        Parameters:
            - endpoint string The relative URI that comes directly after
            your API key in the BigDoor documentation.

            - params dict The parameters to be sent via the GET query string.
        """
        r = self.do_request('get', endpoint, params)
        return json.loads(r.body_string())

    def delete(self, endpoint, params=None):
        """Sends a DELETE request to the API.

        Parameters:
            - endpoint string The relative URI that comes directly after
            your API key in the BigDoor documentation.

            - params dict The parameters to be sent via the GET query string.
        """
        r = self.do_request('delete', endpoint, params)

    def post(self, endpoint, params=None, payload=None):
        """Sends a POST request to the API and returns a native data
        structure from the JSON response.

        Parameters:
            - endpoint string The relative URI that comes directly after
            your API key in the BigDoor documentation.

            - params dict The parameters to be sent via the GET query string.

            - payload dict The data to be sent via the POST body
        """
        r = self.do_request('post', endpoint, params, payload)
        return json.loads(r.body_string())

    def put(self, endpoint, params=None, payload=None):
        """Sends a PUT request to the API and returns a native data
        structure from the JSON response.

        Parameters:
            - endpoint string The relative URI that comes directly after
            your API key in the BigDoor documentation.

            - params dict The parameters to be sent via the GET query string.

            - payload dict The data to be sent via the POST body
        """
        r = self.do_request('put', endpoint, params, payload)
        return json.loads(r.body_string())
