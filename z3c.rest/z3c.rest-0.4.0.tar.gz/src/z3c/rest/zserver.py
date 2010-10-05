##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

$Id: zserver.py 117231 2010-10-05 06:45:47Z icemac $
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
