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
"""REST server factories for Twisted

Note: The file is not named twisted.py because of package import problems.

$Id: twist.py 82045 2007-11-30 11:40:12Z srichter $
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
