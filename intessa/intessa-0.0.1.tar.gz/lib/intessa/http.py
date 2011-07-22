"""
Code responsible for low-level HTTP interactions.

At the moment this just contains the default HTTP backend for
:class:`intessa.API`, based on the requests_ library for Python.

.. _requests: http://python-requests.org/
"""

from requests import request

from intessa.response import Response


def requests_http_backend(api, method, url, *args, **kwargs):
    """Shim over ``requests.request`` to return :class:`Responses <intessa.response.Response>`."""

    http_response = request(method, url, *args, **kwargs)
    return Response(api=api,
                    status_code=http_response.status_code,
                    headers=http_response.headers,
                    content=http_response.content)
