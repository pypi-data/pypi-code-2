##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""REST server factories

$Id: zserver.py 82045 2007-11-30 11:40:12Z srichter $
"""
from zope.server.http.commonaccesslogger import CommonAccessLogger
from zope.server.http import wsgihttpserver
from zope.app.server.wsgi import ServerType
from zope.app.wsgi import WSGIPublisherApplication
from z3c.rest.rest import RESTPublicationRequestFactory

rest = ServerType(wsgihttpserver.WSGIHTTPServer,
                  WSGIPublisherApplication,
                  CommonAccessLogger,
                  8080, True,
                  RESTPublicationRequestFactory)
