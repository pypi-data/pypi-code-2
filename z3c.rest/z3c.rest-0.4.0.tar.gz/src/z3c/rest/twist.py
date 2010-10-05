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
"""REST server factories for Twisted

Note: The file is not named twisted.py because of package import problems.

$Id: twist.py 117231 2010-10-05 06:45:47Z icemac $
"""
from twisted.web2 import log, server, wsgi
from twisted.web2.channel.http import HTTPFactory
from zope.app.twisted import http
from zope.app.twisted.server import ServerType
from zope.app.wsgi import WSGIPublisherApplication
from z3c.rest.rest import RESTPublicationRequestFactory

def createRESTFactory(db):
    resource = wsgi.WSGIResource(
        WSGIPublisherApplication(db, RESTPublicationRequestFactory))
    resource = log.LogWrapperResource(resource)
    resource = http.Prebuffer(resource)

    return HTTPFactory(server.Site(resource))

rest = ServerType(createRESTFactory, 8081)
