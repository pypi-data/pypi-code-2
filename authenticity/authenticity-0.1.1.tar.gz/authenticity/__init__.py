# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
HTTP request dispatcher.
"""

from __future__ import absolute_import, division, print_function

__all__ = ['__version__', 'mp_handler']

__version__  = '0.1.1'
__homepage__ = 'http://projects.cnix.ro/authenticity'


def mp_handler(req):
    from authenticity.handler import RequestHandler
    request_handler = RequestHandler()
    return request_handler.handle_request(req)


