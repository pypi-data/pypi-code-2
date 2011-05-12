# LinkExchange.Django - Django integration with LinkExchange library
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

from django.http import Http404, HttpResponse

from linkexchange_django import support

def handle_request(request):
    if support.platform is None:
        raise Http404

    page_request = support.convert_request(request)
    page_response = support.platform.handle_request(page_request)

    if page_response.status == 404 and not page_response.body:
        raise Http404

    headers = page_response.headers.copy()
    response = HttpResponse(page_response.body,
            content_type=headers.pop('Content-Type', 'text/html'),
            status=page_response.status)
    for k, v in headers.items():
        response[k] = v

    return response
