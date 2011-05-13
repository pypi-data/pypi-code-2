# LinkExchange.TurboGears - TurboGears 1.x integration with LinkExchange
# library
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

from cherrypy import request, response, NotFound
from turbogears import expose
from turbogears.controllers import Controller

from linkexchange.turbogears import support

class LinkExchangeHandler(Controller):
    @expose()
    def default(self, *args, **kw):
        if support.platform is None:
            raise NotFound()

        page_request = support.convert_request(request)
        page_response = support.platform.handle_request(page_request)

        response.status = page_response.status
        response.headerMap.update(response.headers)

        return page_response.body
