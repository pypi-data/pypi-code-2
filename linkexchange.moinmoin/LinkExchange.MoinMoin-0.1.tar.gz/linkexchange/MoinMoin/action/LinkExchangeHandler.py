# LinkExchange.MoinMoin - MoinMoin integration with LinkExchange library
# Copyright (C) 2009, 2011 Konstantin Korikov
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

from linkexchange.MoinMoin import support
from linkexchange.MoinMoin.support import moin_version

def status_msg(status):
    if status == 404:
        return 'Not found'
    elif status == 200:
        return 'OK'
    return None

def execute(pagename, request):
    cfg = request.cfg
    if moin_version < (1, 9):
        uri = request.form.get('uri', ['/'])[0]
    else:
        uri = request.values.get('uri', '/')

    try:
        platform = cfg.linkexchange_platform
    except AttributeError:
        support.configure(cfg)
        platform = cfg.linkexchange_platform

    lx_request = support.convert_request(request)
    lx_request.uri = uri
    lx_response = platform.handle_request(lx_request)

    if moin_version < (1, 6):
        from MoinMoin.util import MoinMoinNoFooter
        request.http_headers(['Status: %d %s' % (
            lx_response.status, status_msg(lx_response.status) or '')])
        request.setResponseCode(lx_request.status)
        request.http_headers(['%s: %s' % (k, v)
            for k, v in lx_response.headers.items()])
        request.write(lx_response.body)
        raise MoinMoinNoFooter
    elif moin_version < (1, 9):
        headers = ['Status: %d %s' % (
            lx_response.status, status_msg(lx_response.status) or '')]
        headers.extend(['%s: %s' % (k, v)
            for k, v in lx_response.headers.items()])
        request.emit_http_headers(headers)
        request.write(lx_response.body)
    else:
        request.status_code = lx_response.status
        for k, v in lx_response.headers.items():
            request.headers[k] = v
        request.write(lx_response.body)
