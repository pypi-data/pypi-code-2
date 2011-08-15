"""
Code responsible for low-level HTTP interactions.

At the moment this just contains the default HTTP backend for
:class:`intessa.API`, based on the requests_ library for Python.

.. _requests: http://python-requests.org/
"""

from requests import request

from intessa.conneg.default import DEFAULT_REGISTER
from intessa.response import Response


def requests_http_backend(api, method, url, *args, **kwargs):
    """Shim over ``requests.request`` to return :class:`Responses <intessa.response.Response>`."""

    codec_register = kwargs.pop('codec_register', DEFAULT_REGISTER)
    http_response = request(method, url, *args, **kwargs)
    # This will only raise URLErrors related to connection issues, not HTTP
    # error codes.
    if http_response.error:
        raise http_response.error
    return Response(api=api,
                    status_code=http_response.status_code,
                    headers=http_response.headers,
                    content=http_response.content,
                    codec_register=codec_register)
