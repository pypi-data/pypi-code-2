# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os

from qt import QtNetwork

def set_proxy():
    for key, value in os.environ.items():
        if key in ["http_proxy", "HTTP_PROXY"]:
            if value.startswith("http://"):
                value = value[7:]

            host = value.split(":")[0]
            port = int(value[:-1].split(":")[1])
            print host, port

            proxy = QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.HttpProxy)
            proxy.setHostName(host)
            proxy.setPort(port)
            QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
