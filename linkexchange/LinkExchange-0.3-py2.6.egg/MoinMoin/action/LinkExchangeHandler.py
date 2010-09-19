# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

# You may use this action plugin in comination with mod_rewrite. For example:
#
#  RewriteEngine on
#  RewriteRule ^(/articles/.+)$ /?action=LinkExchangeHandler&uri=$1 [PT]

try:
    from MoinMoin.util import MoinMoinNoFooter
except ImportError:
    MoinMoinNoFooter = None

from linkexchange.MoinMoin import support

def execute(pagename, request):
    cfg = request.cfg
    uri = request.form.get('uri', ['/'])[0]

    try:
        platform = cfg.linkexchange_platform
    except AttributeError:
        support.configure(cfg)
        platform = cfg.linkexchange_platform

    page_request = support.convert_request(request)
    page_request.uri = uri
    page_response = platform.handle_request(page_request)

    try:
        emit_http_headers = request.emit_http_headers
    except AttributeError:
        emit_http_headers = request.http_headers
    try:
        set_response_code = request.setResponseCode
    except AttributeError:
        set_response_code = lambda x: None

    set_response_code(page_response.status)
    headers = []
    if page_response.status == 404:
        headers.append('Status: 404 Not found')
    elif page_response.status == 200:
        headers.append('Status: 200 OK')
    else:
        headers.append('Status: %d' % page_response.status)
    headers.extend(['%s: %s' % (k, v)
        for k, v in page_response.headers.items()])
    emit_http_headers(headers)
    request.write(page_response.body)

    if MoinMoinNoFooter is not None:
        raise MoinMoinNoFooter
